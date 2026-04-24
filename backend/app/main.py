"""
Funding Aggregator - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.database import init_db
from app.core.logging import setup_logging
from app.api.v1 import router as api_v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Funding Aggregator API",
    description="""
🚀 **Funding Aggregator** — AI-powered aggregator for grants, scholarships, and funding opportunities.

## Features
- 🔍 **Smart Search**: Full-text and AI-powered natural language search
- 🤖 **AI Analysis**: Automatic keyword extraction, summarization, and categorization
- 📊 **Rich Filtering**: Filter by category, source, amount, deadline, country
- ⭐ **Favorites**: Save and manage favorite grants
- 🔐 **JWT Auth**: Secure API access with token-based authentication
- 📈 **Metrics**: Prometheus metrics and Grafana dashboards

## Authentication
Most endpoints are public for reading. Writing operations require JWT authentication.
Use `/api/v1/auth/register` and `/api/v1/auth/login` to get tokens.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation
Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    excluded_handlers=["/metrics", "/health"],
    env_var_name="ENABLE_METRICS",
).instrument(app).expose(app, include_in_schema=True, tags=["Monitoring"])

# API routes
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — API info."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
