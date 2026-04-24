"""
Funding Aggregator - Base Scraper
"""
import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import get_logger
from app.core.metrics import SCRAPE_COUNT, SCRAPE_DURATION, SCRAPE_RECORDS
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Implements anti-blocking measures, error handling, and retry logic.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent()
        self.request_delay = settings.SCRAPE_REQUEST_DELAY
        self._session: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> dict:
        """Generate randomized headers to avoid detection."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

    async def get_session(self) -> httpx.AsyncClient:
        """Get or create an HTTP session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                headers=self.headers,
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
                limits=httpx.Limits(
                    max_connections=settings.MAX_CONCURRENT_REQUESTS,
                    max_keepalive_connections=5,
                ),
            )
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
            self._session = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page with retry logic and anti-blocking measures.
        """
        # Random delay between requests
        delay = self.request_delay + random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)

        session = await self.get_session()
        
        try:
            # Rotate User-Agent per request
            response = await session.get(url, headers={"User-Agent": self.ua.random})
            response.raise_for_status()
            
            logger.info(
                "page_fetched",
                source=self.source_name,
                url=url[:100],
                status_code=response.status_code,
            )
            return response.text

        except httpx.HTTPStatusError as e:
            logger.warning(
                "http_error",
                source=self.source_name,
                url=url[:100],
                status_code=e.response.status_code,
            )
            if e.response.status_code == 429:
                # Rate limited — wait longer
                await asyncio.sleep(random.uniform(10, 30))
            raise

        except httpx.RequestError as e:
            logger.error(
                "request_error",
                source=self.source_name,
                url=url[:100],
                error=str(e),
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def fetch_json(self, url: str, params: dict = None) -> Optional[dict]:
        """Fetch JSON data from an API endpoint."""
        delay = self.request_delay + random.uniform(0.5, 1.5)
        await asyncio.sleep(delay)

        session = await self.get_session()

        try:
            response = await session.get(
                url,
                params=params,
                headers={**self.headers, "Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(
                "json_fetch_error",
                source=self.source_name,
                url=url[:100],
                error=str(e),
            )
            raise

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """
        Main scraping method — must be implemented by subclasses.
        Returns a list of raw grant dictionaries.
        """
        pass

    async def run(self) -> dict:
        """
        Execute the scraping pipeline with metrics and logging.
        Returns scrape statistics.
        """
        start_time = time.time()
        stats = {
            "source": self.source_name,
            "status": "success",
            "records_found": 0,
            "records_new": 0,
            "records_updated": 0,
            "error": None,
            "duration": 0,
        }

        try:
            logger.info("scrape_started", source=self.source_name)
            results = await self.scrape()
            stats["records_found"] = len(results)
            
            SCRAPE_COUNT.labels(source=self.source_name, status="success").inc()
            logger.info(
                "scrape_completed",
                source=self.source_name,
                records=len(results),
            )

        except Exception as e:
            stats["status"] = "failed"
            stats["error"] = str(e)
            SCRAPE_COUNT.labels(source=self.source_name, status="failed").inc()
            logger.error("scrape_failed", source=self.source_name, error=str(e))

        finally:
            stats["duration"] = time.time() - start_time
            SCRAPE_DURATION.labels(source=self.source_name).observe(stats["duration"])
            await self.close()

        return stats
