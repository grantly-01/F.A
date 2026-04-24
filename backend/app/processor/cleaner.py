"""
Funding Aggregator - Text Cleaner & Normalizer
"""
import re
import html
from typing import Optional
from datetime import datetime, date

from app.core.logging import get_logger

logger = get_logger(__name__)


class TextCleaner:
    """Clean and normalize scraped text data."""

    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and decode entities."""
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"[\t\r]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    @staticmethod
    def extract_amount(text: str) -> Optional[float]:
        """Extract monetary amount from text."""
        if not text:
            return None
        patterns = [
            r"\$\s*([\d,]+(?:\.\d{2})?)",
            r"([\d,]+(?:\.\d{2})?)\s*(?:USD|EUR|GBP)",
            r"(?:up to|max(?:imum)?)\s*\$?\s*([\d,]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))
        return None

    @staticmethod
    def extract_date(text: str) -> Optional[date]:
        """Try to parse a date from various formats."""
        if not text:
            return None
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y",
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y",
            "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(text.strip(), fmt).date()
            except (ValueError, TypeError):
                continue
        return None

    @staticmethod
    def normalize_country(country: str) -> str:
        """Normalize country names."""
        if not country:
            return ""
        mappings = {
            "us": "United States", "usa": "United States",
            "uk": "United Kingdom", "gb": "United Kingdom",
            "eu": "Europe", "de": "Germany", "fr": "France",
        }
        return mappings.get(country.lower().strip(), country.strip().title())

    @staticmethod
    def normalize_currency(currency: str) -> str:
        """Normalize currency codes."""
        if not currency:
            return "USD"
        mappings = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
        return mappings.get(currency.strip(), currency.upper().strip()[:3])


class DataNormalizer:
    """Normalize and validate scraped grant data."""

    def __init__(self):
        self.cleaner = TextCleaner()

    def normalize_grant(self, raw: dict) -> dict:
        """Normalize a raw grant dictionary."""
        return {
            "title": self.cleaner.clean_html(raw.get("title", ""))[:500],
            "description": self.cleaner.normalize_whitespace(
                self.cleaner.clean_html(raw.get("description", ""))
            ),
            "source_url": raw.get("source_url", "").strip()[:2000],
            "source_name": raw.get("source_name", "unknown").lower().strip(),
            "amount_min": self._safe_decimal(raw.get("amount_min")),
            "amount_max": self._safe_decimal(raw.get("amount_max")),
            "currency": self.cleaner.normalize_currency(raw.get("currency", "USD")),
            "deadline": self._ensure_date(raw.get("deadline")),
            "posted_date": self._ensure_date(raw.get("posted_date")),
            "eligibility": self.cleaner.clean_html(raw.get("eligibility", "")),
            "requirements": self.cleaner.clean_html(raw.get("requirements", "")),
            "country": self.cleaner.normalize_country(raw.get("country", "")),
            "region": raw.get("region", "").strip(),
            "status": raw.get("status", "active"),
        }

    @staticmethod
    def _safe_decimal(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _ensure_date(value) -> Optional[date]:
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return TextCleaner.extract_date(value)
        return None
