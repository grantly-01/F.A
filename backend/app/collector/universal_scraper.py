"""
Funding Aggregator — Universal Grant Scraper for Kazakhstan
Scrapes grants from multiple KZ sources with anti-blocking measures.
"""
import asyncio
import hashlib
import random
import re
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional
from bs4 import BeautifulSoup
import httpx
from fake_useragent import UserAgent

from app.core.logging import get_logger
from app.core.metrics import SCRAPE_REQUESTS, SCRAPE_ITEMS

logger = get_logger(__name__)

# KZ Grant sources configuration
SOURCES = {
    "egov_kz": {
        "name": "egov.kz",
        "base_url": "https://egov.kz",
        "search_urls": [
            "https://egov.kz/cms/ru/articles/grants",
            "https://www.gov.kz/memleket/entities/science/activities/grants",
        ],
        "country": "Казахстан",
    },
    "bolashak": {
        "name": "bolashak.gov.kz",
        "base_url": "https://www.bolashak.gov.kz",
        "search_urls": [
            "https://www.bolashak.gov.kz/ru/o-stipendii",
            "https://www.bolashak.gov.kz/ru/programmy",
        ],
        "country": "Казахстан",
    },
    "science_fund": {
        "name": "science-fund.kz",
        "base_url": "https://www.science-fund.kz",
        "search_urls": [
            "https://www.science-fund.kz/grants",
            "https://www.science-fund.kz/competitions",
        ],
        "country": "Казахстан",
    },
    "astana_hub": {
        "name": "astanahub.com",
        "base_url": "https://astanahub.com",
        "search_urls": [
            "https://astanahub.com/ru/programs/grants",
        ],
        "country": "Казахстан",
    },
    "damu": {
        "name": "damu.kz",
        "base_url": "https://damu.kz",
        "search_urls": [
            "https://damu.kz/programmy",
        ],
        "country": "Казахстан",
    },
    "zerde": {
        "name": "zerde.gov.kz",
        "base_url": "https://zerde.gov.kz",
        "search_urls": [
            "https://zerde.gov.kz/activity/projects",
        ],
        "country": "Казахстан",
    },
    "sk_kz": {
        "name": "sk.kz",
        "base_url": "https://sk.kz",
        "search_urls": [
            "https://sk.kz/innovation",
        ],
        "country": "Казахстан",
    },
    "nu_edu": {
        "name": "nu.edu.kz",
        "base_url": "https://nu.edu.kz",
        "search_urls": [
            "https://nu.edu.kz/research/grants",
        ],
        "country": "Казахстан",
    },
    "undp_kz": {
        "name": "undp.org",
        "base_url": "https://www.undp.org",
        "search_urls": [
            "https://www.undp.org/kazakhstan/grants",
            "https://procurement-notices.undp.org/view_notices.cfm?Country=KAZ",
        ],
        "country": "Казахстан",
    },
    "usaid_kz": {
        "name": "usaid.gov",
        "base_url": "https://www.usaid.gov",
        "search_urls": [
            "https://www.usaid.gov/kazakhstan/work-with-us/find-a-funding-opportunity",
        ],
        "country": "Казахстан",
    },
    "erasmus_kz": {
        "name": "erasmusplus.kz",
        "base_url": "https://erasmusplus.kz",
        "search_urls": [
            "https://erasmusplus.kz/mobility",
        ],
        "country": "Казахстан",
    },
    "british_council_kz": {
        "name": "britishcouncil.kz",
        "base_url": "https://www.britishcouncil.kz",
        "search_urls": [
            "https://www.britishcouncil.kz/programmes/education/newton-al-farabi",
        ],
        "country": "Казахстан",
    },
    "soros_kz": {
        "name": "soros.kz",
        "base_url": "https://www.soros.kz",
        "search_urls": [
            "https://www.soros.kz/grants",
        ],
        "country": "Казахстан",
    },
    "kazaid": {
        "name": "kazaid.kz",
        "base_url": "https://kazaid.kz",
        "search_urls": [
            "https://kazaid.kz/grants",
        ],
        "country": "Казахстан",
    },
    "qazinnovations": {
        "name": "qazinnovations.gov.kz",
        "base_url": "https://qazinnovations.gov.kz",
        "search_urls": [
            "https://qazinnovations.gov.kz/grants",
        ],
        "country": "Казахстан",
    },
    "elumiti": {
        "name": "elumiti.kz",
        "base_url": "https://elumiti.kz",
        "search_urls": [
            "https://elumiti.kz/scholarships",
        ],
        "country": "Казахстан",
    },
}


class UniversalScraper:
    """
    Universal grant scraper with anti-blocking measures.
    Supports multiple Kazakhstan grant sources.
    """

    def __init__(self):
        self.ua = UserAgent()
        self.results = []
        self.seen_hashes = set()

    def _get_headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,kk;q=0.8,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.kz/",
            "Connection": "keep-alive",
        }

    def _content_hash(self, title: str, source: str) -> str:
        return hashlib.md5(f"{title.lower().strip()}{source}".encode()).hexdigest()

    def _extract_amount(self, text: str) -> tuple[Optional[Decimal], Optional[Decimal], str]:
        """Extract funding amounts from text. Returns (min, max, currency)."""
        text = text.replace("\xa0", " ").replace(",", "")
        # KZT / тенге patterns
        kzt = re.findall(r'(\d[\d\s]*(?:\.\d+)?)\s*(?:тенге|теңге|₸|тг|KZT|млн\.?\s*(?:тенге|теңге|₸|тг))', text, re.I)
        if kzt:
            amounts = []
            for m in kzt:
                val = re.sub(r'\s+', '', m)
                try:
                    num = Decimal(val)
                    if 'млн' in text[text.lower().find(val):text.lower().find(val)+20].lower():
                        num *= 1000000
                    amounts.append(num)
                except Exception:
                    pass
            if amounts:
                return (min(amounts), max(amounts), "KZT")
        # USD patterns
        usd = re.findall(r'\$\s*(\d[\d\s,]*(?:\.\d+)?)', text)
        if usd:
            amounts = []
            for m in usd:
                try:
                    amounts.append(Decimal(re.sub(r'[\s,]', '', m)))
                except Exception:
                    pass
            if amounts:
                return (min(amounts), max(amounts), "USD")
        return (None, None, "KZT")

    def _extract_deadline(self, text: str) -> Optional[date]:
        """Extract deadline date from text."""
        patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](20\d{2})',
            r'(20\d{2})-(\d{1,2})-(\d{1,2})',
            r'до\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(20\d{2})',
        ]
        months_ru = {"января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,
                     "июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12}

        for i, pat in enumerate(patterns):
            m = re.search(pat, text, re.I)
            if m:
                try:
                    if i == 0:
                        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                    elif i == 1:
                        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    elif i == 2:
                        month_num = months_ru.get(m.group(2).lower(), 1)
                        return date(int(m.group(3)), month_num, int(m.group(1)))
                except ValueError:
                    pass
        return None

    def _clean_text(self, html_text: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def _fetch_page(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Fetch a page with retries and anti-blocking delays."""
        for attempt in range(3):
            try:
                await asyncio.sleep(random.uniform(1.5, 4.0))
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=30.0,
                    follow_redirects=True,
                )
                if response.status_code == 200:
                    SCRAPE_REQUESTS.labels(source=url[:50], status="success").inc()
                    return response.text
                elif response.status_code in (403, 429):
                    logger.warning("scrape_blocked", url=url, status=response.status_code, attempt=attempt)
                    await asyncio.sleep(random.uniform(5, 15))
                else:
                    logger.warning("scrape_http_error", url=url, status=response.status_code)
            except Exception as e:
                logger.error("scrape_fetch_error", url=url, error=str(e), attempt=attempt)
                await asyncio.sleep(random.uniform(2, 5))
        SCRAPE_REQUESTS.labels(source=url[:50], status="failed").inc()
        return None

    def _parse_generic_page(self, html: str, source_config: dict, url: str) -> list[dict]:
        """Generic HTML parser — extracts grant-like content from any page."""
        soup = BeautifulSoup(html, "html.parser")
        grants = []
        # Look for article/card elements
        selectors = [
            "article", ".card", ".grant", ".grant-item", ".post",
            ".news-item", ".program", ".program-item", ".list-item",
            "[class*='grant']", "[class*='program']", "[class*='competition']",
        ]
        items = []
        for sel in selectors:
            items = soup.select(sel)
            if items:
                break
        if not items:
            items = soup.select("div.row > div, .content-block, main section")
        if not items:
            # Fallback: treat the whole page as one grant
            title_el = soup.find("h1") or soup.find("title")
            if title_el:
                title = self._clean_text(str(title_el))
                desc_parts = [self._clean_text(str(p)) for p in soup.find_all("p")[:5]]
                desc = " ".join(desc_parts)[:2000]
                if len(title) > 10 and len(desc) > 30:
                    grants.append(self._build_grant(title, desc, url, source_config))
            return grants

        for item in items[:30]:
            heading = item.find(["h1", "h2", "h3", "h4", "a"])
            if not heading:
                continue
            title = self._clean_text(str(heading))
            if len(title) < 8:
                continue
            paragraphs = item.find_all("p")
            desc = " ".join([self._clean_text(str(p)) for p in paragraphs])[:2000]
            if not desc:
                desc = self._clean_text(str(item))[:1500]
            link_el = item.find("a", href=True)
            link = link_el["href"] if link_el else url
            if link.startswith("/"):
                link = source_config["base_url"] + link
            grant = self._build_grant(title, desc, link, source_config)
            if grant:
                grants.append(grant)

        return grants

    def _build_grant(self, title: str, description: str, url: str, source_config: dict) -> Optional[dict]:
        """Build a grant dict from extracted data."""
        content_hash = self._content_hash(title, source_config["name"])
        if content_hash in self.seen_hashes:
            return None
        self.seen_hashes.add(content_hash)

        amount_min, amount_max, currency = self._extract_amount(f"{title} {description}")
        deadline = self._extract_deadline(f"{title} {description}")

        return {
            "title": title[:500],
            "description": description[:4000] if description else None,
            "source_url": url,
            "source_name": source_config["name"],
            "amount_min": amount_min,
            "amount_max": amount_max,
            "currency": currency,
            "deadline": deadline,
            "posted_date": date.today(),
            "country": source_config.get("country", "Казахстан"),
            "status": "active",
            "scraped_at": datetime.now(timezone.utc),
        }

    async def scrape_source(self, source_key: str) -> list[dict]:
        """Scrape a single source."""
        config = SOURCES.get(source_key)
        if not config:
            return []
        grants = []
        async with httpx.AsyncClient(verify=False) as client:
            for url in config["search_urls"]:
                logger.info("scraping_url", source=source_key, url=url)
                html = await self._fetch_page(client, url)
                if html:
                    parsed = self._parse_generic_page(html, config, url)
                    grants.extend([g for g in parsed if g])
                    logger.info("scraped_page", source=source_key, url=url, count=len(parsed))
        SCRAPE_ITEMS.labels(source=source_key).inc(len(grants))
        return grants

    async def scrape_all(self) -> list[dict]:
        """Scrape all configured sources."""
        all_grants = []
        for source_key in SOURCES:
            try:
                grants = await self.scrape_source(source_key)
                all_grants.extend(grants)
                logger.info("source_complete", source=source_key, total=len(grants))
            except Exception as e:
                logger.error("source_error", source=source_key, error=str(e))
        logger.info("scrape_all_complete", total=len(all_grants), sources=len(SOURCES))
        return all_grants

    @staticmethod
    def get_source_count() -> int:
        return len(SOURCES)

    @staticmethod
    def get_source_names() -> list[str]:
        return [s["name"] for s in SOURCES.values()]
