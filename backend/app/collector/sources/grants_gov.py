"""
Funding Aggregator - Grants.gov Scraper
Scrapes funding opportunities from the Grants.gov API.
"""
from datetime import datetime
from typing import Optional

from app.collector.base_scraper import BaseScraper
from app.core.logging import get_logger

logger = get_logger(__name__)

# Grants.gov API endpoint
GRANTS_GOV_API = "https://www.grants.gov/grantsws/rest/opportunities/search/"


class GrantsGovScraper(BaseScraper):
    """
    Scraper for Grants.gov — the largest federal grants database in the US.
    Uses their public REST API.
    """

    def __init__(self):
        super().__init__(source_name="grants.gov")
        self.api_url = GRANTS_GOV_API
        self.page_size = 25

    async def scrape(self) -> list[dict]:
        """Scrape grants from Grants.gov API."""
        all_grants = []
        
        # Search for various keywords to get diverse results
        keywords = [
            "research", "science", "technology", "education",
            "innovation", "health", "environment", "engineering",
        ]

        for keyword in keywords:
            try:
                grants = await self._search_grants(keyword)
                all_grants.extend(grants)
                logger.info(
                    "grants_gov_keyword_done",
                    keyword=keyword,
                    count=len(grants),
                )
            except Exception as e:
                logger.warning(
                    "grants_gov_keyword_failed",
                    keyword=keyword,
                    error=str(e),
                )
                continue

        # Deduplicate by opportunity ID
        seen = set()
        unique = []
        for grant in all_grants:
            if grant.get("source_url") not in seen:
                seen.add(grant.get("source_url"))
                unique.append(grant)

        logger.info("grants_gov_total", total=len(unique))
        return unique

    async def _search_grants(self, keyword: str, page: int = 1) -> list[dict]:
        """Search grants by keyword via Grants.gov API."""
        params = {
            "keyword": keyword,
            "oppStatuses": "forecasted|posted",
            "sortBy": "openDate|desc",
            "rows": self.page_size,
            "startRecordNum": (page - 1) * self.page_size,
        }

        try:
            data = await self.fetch_json(self.api_url, params=params)
            if not data:
                return []

            opportunities = data.get("oppHits", [])
            return [self._parse_opportunity(opp) for opp in opportunities if opp]

        except Exception as e:
            logger.error("grants_gov_search_error", keyword=keyword, error=str(e))
            return []

    def _parse_opportunity(self, opp: dict) -> dict:
        """Parse a single Grants.gov opportunity into our schema."""
        opp_id = opp.get("id", "")
        
        # Parse dates
        close_date = None
        if opp.get("closeDate"):
            try:
                close_date = datetime.strptime(
                    opp["closeDate"], "%m/%d/%Y"
                ).date()
            except (ValueError, TypeError):
                pass

        open_date = None
        if opp.get("openDate"):
            try:
                open_date = datetime.strptime(
                    opp["openDate"], "%m/%d/%Y"
                ).date()
            except (ValueError, TypeError):
                pass

        # Parse award amounts
        amount_min = None
        amount_max = None
        award_ceiling = opp.get("awardCeiling")
        award_floor = opp.get("awardFloor")
        if award_floor and str(award_floor).replace(".", "").isdigit():
            amount_min = float(award_floor)
        if award_ceiling and str(award_ceiling).replace(".", "").isdigit():
            amount_max = float(award_ceiling)

        return {
            "title": opp.get("title", "Untitled"),
            "description": opp.get("description", ""),
            "source_url": f"https://www.grants.gov/search-results-detail/{opp_id}",
            "source_name": "grants.gov",
            "amount_min": amount_min,
            "amount_max": amount_max,
            "currency": "USD",
            "deadline": close_date,
            "posted_date": open_date,
            "eligibility": opp.get("eligibilities", ""),
            "country": "United States",
            "status": "active" if opp.get("oppStatus") == "posted" else "forecasted",
        }
