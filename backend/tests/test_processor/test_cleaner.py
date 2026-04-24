"""
Funding Aggregator - Processor Tests
"""
import pytest
from app.processor.cleaner import TextCleaner, DataNormalizer


class TestTextCleaner:
    def test_clean_html(self):
        assert TextCleaner.clean_html("<p>Hello <b>World</b></p>") == "Hello World"
        assert TextCleaner.clean_html("&amp; &lt; &gt;") == "& < >"
        assert TextCleaner.clean_html("") == ""

    def test_normalize_whitespace(self):
        assert TextCleaner.normalize_whitespace("  hello   world  ") == "hello world"
        assert TextCleaner.normalize_whitespace("a\n\n\n\nb") == "a\n\nb"

    def test_extract_amount(self):
        assert TextCleaner.extract_amount("$50,000") == 50000.0
        assert TextCleaner.extract_amount("up to $100,000") == 100000.0
        assert TextCleaner.extract_amount("25000 USD") == 25000.0
        assert TextCleaner.extract_amount("no amount") is None

    def test_extract_date(self):
        d = TextCleaner.extract_date("2025-03-15")
        assert d is not None
        assert d.year == 2025
        assert TextCleaner.extract_date("invalid") is None

    def test_normalize_country(self):
        assert TextCleaner.normalize_country("us") == "United States"
        assert TextCleaner.normalize_country("uk") == "United Kingdom"
        assert TextCleaner.normalize_country("Germany") == "Germany"

    def test_normalize_currency(self):
        assert TextCleaner.normalize_currency("$") == "USD"
        assert TextCleaner.normalize_currency("€") == "EUR"
        assert TextCleaner.normalize_currency("GBP") == "GBP"


class TestDataNormalizer:
    def test_normalize_grant(self):
        normalizer = DataNormalizer()
        raw = {
            "title": "<b>Test Grant</b>",
            "description": "  Some description  ",
            "source_url": "https://example.com/grant1",
            "source_name": "  Test Source  ",
            "amount_min": "1000",
            "currency": "$",
            "country": "us",
        }
        result = normalizer.normalize_grant(raw)
        assert result["title"] == "Test Grant"
        assert result["source_name"] == "test source"
        assert result["amount_min"] == 1000.0
        assert result["currency"] == "USD"
        assert result["country"] == "United States"
