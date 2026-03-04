import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sqlalchemy.orm import Session
from datetime import datetime
import openai
from dotenv import load_dotenv

from .models import Grant
from .schemas import GrantInfo

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _extract_grant_no_ai(html: str, source_url: str) -> GrantInfo | None:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    h1 = soup.find("h1")
    title = (h1.get_text(strip=True) if h1 else None) or (soup.title.get_text(strip=True) if soup.title else None)
    if not title:
        return None

    meta = soup.find("meta", attrs={"name": "description"})
    description = meta.get("content") if meta and meta.get("content") else None
    if not description:
        description = (text[:500] + "...") if len(text) > 500 else text

    # Примитивное извлечение сумм: берём большие числа как суммы в тенге
    number_candidates = []
    for raw in re.findall(r"(\d[\d\s]{4,})", text):
        cleaned = int(re.sub(r"\s+", "", raw))
        # отсеиваем явный шум, оставляем только суммы больше 100 000
        if cleaned >= 100_000:
            number_candidates.append(cleaned)

    amount_min = None
    amount_max = None
    if number_candidates:
        amount_max = max(number_candidates)
        if len(number_candidates) > 1:
            amount_min = min(number_candidates)

    host = source_url.split("/")[2] if "://" in source_url else source_url

    return GrantInfo(
        title=title[:250],
        description=(description or "")[:1000],
        funder=host[:200],
        category="grant",
        amount_min=amount_min,
        amount_max=amount_max,
        currency="KZT",
        deadline=None,
        eligibility="Смотрите условия на странице источника.",
        country="KZ",
        status="active",
    )

KEYWORDS = [
    # англ/рус базовые по грантам и субсидиям
    "grant", "грант",
    "subsid", "субсид",
    "fund", "funding",
    "финанс", "поддерж",

    # стипендии и обучение
    "scholar", "stipend", "стипенд",
    "universit", "университ",
    "student", "студент",
    "bachelor", "бакалавр",
    "master", "магистр",
    "phd", "докторант",

    # школьники, олимпиады, ЕНТ
    "school", "школьн",
    "olymp", "олимпиад",
    "ent", "ент",

    # конкурсы и программы
    "конкурс", "программа", "подпрограмма",
]

BASE_SITES = [
    "https://www.gov.kz",
    "https://damu.kz",
    "https://sk.kz",
    "https://baiterek.gov.kz",
    "https://bolashak.gov.kz"
]

TEST_URLS = BASE_SITES

# Лимит глубины обхода на один сайт, чтобы не утащить весь портал gov.kz
MAX_PAGES_PER_SITE = 200


def extract_grant(html: str, source_url: str):
    # Если ключа нет или клиент не инициализирован — используем простую эвристику
    if client is None:
        return _extract_grant_no_ai(html, source_url)

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)[:6000]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=1,
            messages=[
                {
                    "role": "system",
                    "content": """
Ты эксперт по государственным и частным программам финансирования в Казахстане.

Извлекай ТОЛЬКО программы, действующие в Республике Казахстан.
Игнорируй международные гранты.

Категории:
- grant
- subsidy
- scholarship
- financing
- support_program

Дедлайн формат YYYY-MM-DD.
"""
                },
                {
                    "role": "user",
                    "content": f"Текст:\n{text}\n\nИсточник: {source_url}"
                }
            ],
            response_format=GrantInfo,
        )

        parsed = response.choices[0].message.parsed
        # Модель может вернуть null по инструкции — тогда пробуем простой парсер
        if parsed is None:
            return _extract_grant_no_ai(html, source_url)

        return parsed

    except Exception as e:
        print("GPT error:", e)
        # При любой ошибке пытаемся вытащить хотя бы базовую информацию без AI
        return _extract_grant_no_ai(html, source_url)


def save_grant(db: Session, grant_info: GrantInfo, url: str, raw_html: str):

    existing = db.query(Grant).filter(Grant.source_url == url).first()
    if existing:
        return None

    deadline = None
    if grant_info.deadline:
        try:
            deadline = datetime.strptime(grant_info.deadline, "%Y-%m-%d").date()
        except:
            pass

    grant = Grant(
        title=grant_info.title[:500],
        description=grant_info.description[:2000],
        funder=grant_info.funder[:200],
        category=grant_info.category,
        amount_min=grant_info.amount_min,
        amount_max=grant_info.amount_max,
        currency=grant_info.currency,
        deadline=deadline,
        eligibility=grant_info.eligibility[:1000],
        country="KZ",
        source_url=url,
        source_raw=raw_html[:5000],
        status="active"
    )

    db.add(grant)
    db.commit()
    db.refresh(grant)

    return grant


def collect_from_site(db: Session, base_url: str):
    """
    Более глубокий обход: идём вглубь по ссылкам внутри домена,
    собираем все страницы, в чьём href есть ключевые слова.
    """
    headers = {"User-Agent": "Mozilla/5.0"}

    visited: set[str] = set()
    to_visit: list[str] = [base_url]

    base_host = urlparse(base_url).netloc

    while to_visit and len(visited) < MAX_PAGES_PER_SITE:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, headers=headers, timeout=30)
        except Exception as e:
            print("Collection error (fetch):", e)
            continue

        html = response.text

        # Пытаемся извлечь грант с этой страницы
        try:
            grant_info = extract_grant(html, url)
            if grant_info:
                save_grant(db, grant_info, url, html)
        except Exception as e:
            print("Collection error (parse):", e)

        # Собираем новые ссылки для обхода
        try:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                href_lower = href.lower()

                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                # Ходим только внутри того же домена
                if parsed.netloc != base_host:
                    continue

                # Только ссылки, похожие на гранты/программы
                if not any(word in href_lower for word in KEYWORDS):
                    continue

                if full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

        except Exception as e:
            print("Collection error (links):", e)


def run_full_collection(db: Session):

    for site in BASE_SITES:
        print(f"Scanning {site}")
        collect_from_site(db, site)

    update_expired(db)


def update_expired(db: Session):

    today = datetime.today().date()

    grants = db.query(Grant).filter(Grant.deadline != None).all()

    for g in grants:
        if g.deadline < today:
            g.status = "closed"

    db.commit()


def collect_from_url(db: Session, url: str) -> bool:
    try:
        response = requests.get(url, timeout=30)
        grant_info = extract_grant(response.text, url)

        if grant_info:
            save_grant(db, grant_info, url, response.text)
            return True

    except Exception as e:
        print("Collection error:", e)

    return False