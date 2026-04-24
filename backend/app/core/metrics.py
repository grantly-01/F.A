"""
Funding Aggregator - Prometheus Metrics
"""
from prometheus_client import Counter, Histogram, Gauge

# API Metrics
REQUEST_COUNT = Counter(
    "funding_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "funding_api_request_duration_seconds",
    "API request latency",
    ["method", "endpoint"]
)

# Scraping Metrics
SCRAPE_COUNT = Counter(
    "funding_scrape_total",
    "Total scrape operations",
    ["source", "status"]
)

SCRAPE_DURATION = Histogram(
    "funding_scrape_duration_seconds",
    "Scrape operation duration",
    ["source"]
)

SCRAPE_RECORDS = Counter(
    "funding_scrape_records_total",
    "Total records scraped",
    ["source", "type"]  # type: new, updated
)

# Database Metrics
DB_GRANTS_TOTAL = Gauge(
    "funding_grants_total",
    "Total grants in database",
    ["status"]
)

DB_USERS_TOTAL = Gauge(
    "funding_users_total",
    "Total users in database"
)

# AI Metrics
AI_REQUESTS = Counter(
    "funding_ai_requests_total",
    "Total AI API requests",
    ["operation", "status"]  # operation: keywords, summary, search, categorize
)

AI_LATENCY = Histogram(
    "funding_ai_request_duration_seconds",
    "AI API request latency",
    ["operation"]
)
