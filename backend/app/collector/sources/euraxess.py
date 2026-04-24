"""
Funding Aggregator - EURAXESS Scraper
Scrapes European research funding opportunities from EURAXESS.
"""
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from app.collector.base_scraper import BaseScraper
from app.core.logging import get_logger

logger = get_logger(__name__)

EURAXESS_BASE = "https://euraxess.ec.europa.eu"
EURAXESS_SEARCH = f"{EURAXESS_BASE}/jobs/search"


class EuraxessScraper(BaseScraper):
    """
    Scraper for EURAXESS — European Commission's platform for
    research careers and funding opportunities.
    Uses HTML scraping (no public API available).
    """

    def __init__(self):
        super().__init__(source_name="euraxess")

    async def scrape(self) -> list[dict]:
        """Scrape funding opportunities from EURAXESS."""
        all_grants = []
        
        # Scrape multiple pages
        for page in range(0, 3):  # First 3 pages
            try:
                grants = await self._scrape_page(page)
                all_grants.extend(grants)
                logger.info("euraxess_page_done", page=page, count=len(grants))
            except Exception as e:
                logger.warning("euraxess_page_failed", page=page, error=str(e))
                continue

        return all_grants

    async def _scrape_page(self, page: int = 0) -> list[dict]:
        """Scrape a single listing page."""
        url = f"{EURAXESS_SEARCH}?page={page}"
        
        html = await self.fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        listings = soup.select(".views-row")  # Adjust selector based on actual HTML
        
        grants = []
        for listing in listings:
            try:
                grant = self._parse_listing(listing)
                if grant:
                    grants.append(grant)
            except Exception as e:
                logger.warning("euraxess_parse_error", error=str(e))
                continue

        return grants

    def _parse_listing(self, element) -> Optional[dict]:
        """Parse a single EURAXESS listing element."""
        title_el = element.select_one("h2 a, .title a, .views-field-title a")
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        link = title_el.get("href", "")
        if link and not link.startswith("http"):
            link = f"{EURAXESS_BASE}{link}"

        # Try to extract other fields
        description = ""
        desc_el = element.select_one(".field-content, .views-field-body")
        if desc_el:
            description = desc_el.get_text(strip=True)

        country = ""
        country_el = element.select_one(".country, .views-field-country")
        if country_el:
            country = country_el.get_text(strip=True)

        deadline = None
        deadline_el = element.select_one(".deadline, .views-field-field-deadline")
        if deadline_el:
            deadline_text = deadline_el.get_text(strip=True)
            try:
                deadline = datetime.strptime(deadline_text, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                try:
                    deadline = datetime.strptime(deadline_text, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    pass

        return {
            "title": title,
            "description": description,
            "source_url": link,
            "source_name": "euraxess",
            "currency": "EUR",
            "deadline": deadline,
            "country": country or "Europe",
            "region": "Europe",
            "status": "active",
        }
