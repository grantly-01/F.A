"""
Funding Aggregator - Grants API Routes
"""
import uuid
from typing import Optional
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_optional_user
from app.schemas.grant import (
    GrantCreate, GrantUpdate, GrantResponse,
    GrantListResponse, GrantSearchQuery, CategoryResponse
)
from app.services.grant_service import GrantService

router = APIRouter()


@router.get("/", response_model=GrantListResponse)
async def list_grants(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category slug"),
    source: Optional[str] = Query(None, description="Source name"),
    country: Optional[str] = Query(None, description="Country filter"),
    status_filter: Optional[str] = Query("active", alias="status", description="Grant status"),
    amount_min: Optional[Decimal] = Query(None, description="Minimum amount"),
    amount_max: Optional[Decimal] = Query(None, description="Maximum amount"),
    deadline_before: Optional[date] = Query(None, description="Deadline before date"),
    deadline_after: Optional[date] = Query(None, description="Deadline after date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
):
    """
    List grants with filtering, searching, and pagination.
    
    Supports:
    - Full-text search via `q` parameter
    - Filtering by category, source, country, status, amount range, deadline range
    - Sorting by any field
    - Pagination
    """
    params = GrantSearchQuery(
        q=q, category=category, source=source, country=country,
        status=status_filter, amount_min=amount_min, amount_max=amount_max,
        deadline_before=deadline_before, deadline_after=deadline_after,
        page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order,
    )
    service = GrantService(db)
    return await service.get_grants(params)


@router.get("/stats", response_model=dict)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get database statistics (total grants, active, sources)."""
    service = GrantService(db)
    return await service.get_stats()


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all available categories."""
    service = GrantService(db)
    categories = await service.get_categories()
    return categories


@router.get("/sources", response_model=list[str])
async def list_sources(
    db: AsyncSession = Depends(get_db),
):
    """Get all distinct data sources."""
    service = GrantService(db)
    return await service.get_sources()


@router.get("/{grant_id}", response_model=GrantResponse)
async def get_grant(
    grant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single grant by ID."""
    service = GrantService(db)
    grant = await service.get_grant_by_id(grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant


@router.post("/", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
async def create_grant(
    data: GrantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new grant (authenticated users only)."""
    service = GrantService(db)
    grant = await service.create_grant(data)
    return grant


@router.put("/{grant_id}", response_model=GrantResponse)
async def update_grant(
    grant_id: uuid.UUID,
    data: GrantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing grant (authenticated users only)."""
    service = GrantService(db)
    grant = await service.update_grant(grant_id, data)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant


@router.delete("/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grant(
    grant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a grant (authenticated users only)."""
    service = GrantService(db)
    deleted = await service.delete_grant(grant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grant not found")


@router.post("/{grant_id}/favorite", response_model=dict)
async def toggle_favorite(
    grant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle grant as favorite (authenticated users only)."""
    service = GrantService(db)
    
    # Verify grant exists
    grant = await service.get_grant_by_id(grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    is_favorited = await service.toggle_favorite(current_user.id, grant_id)
    return {"favorited": is_favorited}


@router.get("/user/favorites", response_model=GrantListResponse)
async def get_favorites(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's favorite grants."""
    service = GrantService(db)
    return await service.get_user_favorites(current_user.id, page, per_page)


@router.post("/scrape", response_model=dict)
async def trigger_scrape(
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger web scraping from all configured Kazakhstan sources.
    Fetches grants from 16 sources and saves new ones to the database.
    """
    from app.collector.universal_scraper import UniversalScraper
    scraper = UniversalScraper()
    raw_grants = await scraper.scrape_all()

    service = GrantService(db)
    saved = 0
    for g_data in raw_grants:
        try:
            from app.schemas.grant import GrantCreate
            grant_create = GrantCreate(
                title=g_data["title"],
                description=g_data.get("description"),
                source_url=g_data.get("source_url", ""),
                source_name=g_data.get("source_name", "unknown"),
                amount_min=g_data.get("amount_min"),
                amount_max=g_data.get("amount_max"),
                currency=g_data.get("currency", "KZT"),
                deadline=g_data.get("deadline"),
                posted_date=g_data.get("posted_date"),
                eligibility=g_data.get("eligibility"),
                country=g_data.get("country", "Казахстан"),
                status=g_data.get("status", "active"),
            )
            await service.create_grant(grant_create)
            saved += 1
        except Exception:
            pass

    return {
        "scraped": len(raw_grants),
        "saved": saved,
        "sources": scraper.get_source_count(),
        "source_names": scraper.get_source_names(),
    }


@router.post("/ai-process", response_model=dict)
async def ai_process_grants(
    db: AsyncSession = Depends(get_db),
):
    """
    Run Groq AI analysis on all grants that don't have AI summaries yet.
    Generates: keywords, summaries, and category suggestions.
    """
    from app.services.ai_service import get_ai_service
    ai = get_ai_service()
    service = GrantService(db)

    # Get all grants without AI processing
    from sqlalchemy import select
    from app.models.grant import Grant
    stmt = select(Grant).where(Grant.summary_ai.is_(None)).limit(50)
    result = await db.execute(stmt)
    grants = result.scalars().all()

    processed = 0
    errors = 0
    for grant in grants:
        try:
            # Extract keywords
            keywords = ai.extract_keywords(f"{grant.title} {grant.description or ''}")
            if keywords:
                grant.keywords_ai = {"keywords": keywords}

            # Generate summary
            summary = ai.summarize_grant(grant.title, grant.description or "")
            if summary:
                grant.summary_ai = summary

            grant.processed_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
            processed += 1
        except Exception as e:
            errors += 1

    await db.commit()
    return {
        "total_unprocessed": len(grants),
        "processed": processed,
        "errors": errors,
        "ai_available": ai.client is not None,
        "groq_model": get_ai_service().client is not None,
    }
