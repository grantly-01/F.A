import os
import json
from typing import Optional
from pydantic import BaseModel, Field
import openai
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from backend.models import Grant

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class GrantInfo(BaseModel):
    title: str = Field(description="Название гранта/конкурса")
    description: str = Field(description="Краткое описание программы")
    funder: str = Field(description="Название фонда/организации")
    amount_min: Optional[int] = Field(None, description="Минимальная сумма числом")
    amount_max: Optional[int] = Field(None, description="Максимальная сумма числом")
    currency: str = Field(default="KZT", description="Валюта: KZT, USD, EUR")
    deadline: Optional[str] = Field(None, description="Дедлайн в формате YYYY-MM-DD")
    eligibility: str = Field(description="Кто может подать заявку")
    status: str = Field(default="active", description="active или closed")


def extract_grant_with_gpt(html_content: str, source_url: str) -> Optional[GrantInfo]:
    """Извлекает структурированные данные о гранте из HTML с помощью GPT"""

    # Очищаем HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)[:6000]  # Лимит токенов

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты эксперт по грантам в Казахстане. Извлекай точную информацию о грантах. Если сумма не указана точно, используй null. Дедлайн всегда в формате YYYY-MM-DD."
                },
                {
                    "role": "user",
                    "content": f"Извлеки информацию о гранте из текста:\n\n{text[:4000]}\n\nИсточник: {source_url}"
                }
            ],
            response_format=GrantInfo,
            temperature=0.3
        )

        return response.choices[0].message.parsed

    except Exception as e:
        print(f"GPT Error: {e}")
        return None


def save_grant_to_db(db: Session, grant_info: GrantInfo, source_url: str, raw_html: str):
    """Сохраняет грант в базу данных"""

    # Проверка на дубликат по URL
    existing = db.query(Grant).filter(Grant.source_url == source_url).first()
    if existing:
        return None

    from datetime import datetime

    # Парсим дату
    deadline = None
    if grant_info.deadline:
        try:
            deadline = datetime.strptime(grant_info.deadline, "%Y-%m-%d").date()
        except:
            pass

    grant = Grant(
        title=grant_info.title[:500],
        description=grant_info.description[:2000] if grant_info.description else None,
        funder=grant_info.funder[:200] if grant_info.funder else "Unknown",
        amount_min=grant_info.amount_min,
        amount_max=grant_info.amount_max,
        currency=grant_info.currency or "KZT",
        deadline=deadline,
        eligibility=grant_info.eligibility[:1000] if grant_info.eligibility else None,
        source_url=source_url[:500],
        source_raw=raw_html[:5000],  # Обрезаем для экономии места
        status=grant_info.status or "active"
    )

    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant


def collect_from_url(db: Session, url: str) -> bool:
    """Основная функция сбора данных с URL"""

    try:
        # Загружаем страницу
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Извлекаем данные через GPT
        grant_info = extract_grant_with_gpt(response.text, url)

        if not grant_info:
            return False

        # Сохраняем в БД
        result = save_grant_to_db(db, grant_info, url, response.text)
        return result is not None

    except Exception as e:
        print(f"Collection error for {url}: {e}")
        return False


# Тестовые URL для Казахстана
TEST_URLS = [
    "https://www.gov.kz/memleket/entities/gfni/press/article/6e07cf74-5d8f-4b3e-9c2a-1e5d8f4b3e9c",  # ГФНИ
    "https://sk.kz/social",  # Самрук-Казына
]