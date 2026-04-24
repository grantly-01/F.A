"""
Funding Aggregator - Open Grants Scraper
"""
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from app.collector.base_scraper import BaseScraper
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenGrantsScraper(BaseScraper):
    """Scraper for open grant directories."""

    def __init__(self):
        super().__init__(source_name="open_grants")

    async def scrape(self) -> list[dict]:
        all_grants = []
        try:
            data = await self.fetch_json(
                "https://www.research.gov/research-web/api/v1/opportunities"
            )
            if data:
                items = data if isinstance(data, list) else data.get("data", [])
                for item in items:
                    all_grants.append({
                        "title": item.get("title", "Untitled"),
                        "description": item.get("description", ""),
                        "source_url": item.get("url", ""),
                        "source_name": "research.gov",
                        "amount_min": item.get("award_floor"),
                        "amount_max": item.get("award_ceiling"),
                        "currency": "USD",
                        "country": "United States",
                        "status": "active",
                    })
        except Exception as e:
            logger.warning("open_grants_failed", error=str(e))
        return all_grants
