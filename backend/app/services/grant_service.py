"""
Funding Aggregator - Grant Service
"""
import uuid
import math
from typing import Optional
from datetime import date

from sqlalchemy import select, func, or_, text, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grant import Grant, Category, GrantCategory
from app.models.user import UserFavorite
from app.schemas.grant import (
    GrantCreate, GrantUpdate, GrantResponse,
    GrantListResponse, GrantSearchQuery
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class GrantService:
    """Service for managing grants/funding opportunities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_grants(self, params: GrantSearchQuery) -> GrantListResponse:
        """Get paginated and filtered list of grants."""
        query = select(Grant).options(selectinload(Grant.categories))

        # Apply filters
        if params.q:
            # Split query into individual words for better matching
            words = [w.strip() for w in params.q.split() if len(w.strip()) >= 2]
            
            # Full-text search using PostgreSQL tsvector (simple config for any language)
            search_filter = Grant.search_vector.op("@@")(
                func.plainto_tsquery("simple", params.q)
            )
            
            # ILIKE fallback — match ANY word in title, description, eligibility
            like_conditions = []
            for word in (words or [params.q]):
                like_conditions.append(Grant.title.ilike(f"%{word}%"))
                like_conditions.append(Grant.description.ilike(f"%{word}%"))
                like_conditions.append(Grant.eligibility.ilike(f"%{word}%"))
                like_conditions.append(Grant.source_name.ilike(f"%{word}%"))
            
            query = query.where(or_(search_filter, *like_conditions))

        if params.status:
            query = query.where(Grant.status == params.status)

        if params.source:
            query = query.where(Grant.source_name == params.source)

        if params.country:
            query = query.where(Grant.country.ilike(f"%{params.country}%"))

        if params.amount_min is not None:
            query = query.where(
                or_(Grant.amount_min >= params.amount_min, Grant.amount_max >= params.amount_min)
            )

        if params.amount_max is not None:
            query = query.where(
                or_(Grant.amount_max <= params.amount_max, Grant.amount_min <= params.amount_max)
            )

        if params.deadline_after:
            query = query.where(Grant.deadline >= params.deadline_after)

        if params.deadline_before:
            query = query.where(Grant.deadline <= params.deadline_before)

        if params.category:
            query = query.join(Grant.categories).where(Category.slug == params.category)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Sorting
        sort_column = getattr(Grant, params.sort_by, Grant.created_at)
        if params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        offset = (params.page - 1) * params.per_page
        query = query.offset(offset).limit(params.per_page)

        result = await self.db.execute(query)
        grants = result.scalars().unique().all()

        return GrantListResponse(
            items=[GrantResponse.model_validate(g) for g in grants],
            total=total,
            page=params.page,
            per_page=params.per_page,
            pages=math.ceil(total / params.per_page) if total > 0 else 0,
        )

    async def get_grant_by_id(self, grant_id: uuid.UUID) -> Optional[Grant]:
        """Get a single grant by ID."""
        result = await self.db.execute(
            select(Grant)
            .options(selectinload(Grant.categories))
            .where(Grant.id == grant_id)
        )
        return result.scalar_one_or_none()

    async def create_grant(self, data: GrantCreate) -> Grant:
        """Create a new grant."""
        grant_data = data.model_dump(exclude={"category_ids"})
        grant = Grant(**grant_data)

        if data.category_ids:
            categories_result = await self.db.execute(
                select(Category).where(Category.id.in_(data.category_ids))
            )
            grant.categories = list(categories_result.scalars().all())

        self.db.add(grant)
        await self.db.flush()
        await self.db.refresh(grant, attribute_names=["categories"])

        # Update search vector
        await self._update_search_vector(grant)

        logger.info("grant_created", grant_id=str(grant.id), title=grant.title[:50])
        return grant

    async def update_grant(self, grant_id: uuid.UUID, data: GrantUpdate) -> Optional[Grant]:
        """Update an existing grant."""
        grant = await self.get_grant_by_id(grant_id)
        if not grant:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"category_ids"})
        for field, value in update_data.items():
            setattr(grant, field, value)

        if data.category_ids is not None:
            categories_result = await self.db.execute(
                select(Category).where(Category.id.in_(data.category_ids))
            )
            grant.categories = list(categories_result.scalars().all())

        await self.db.flush()
        await self._update_search_vector(grant)
        await self.db.refresh(grant, attribute_names=["categories"])

        logger.info("grant_updated", grant_id=str(grant.id))
        return grant

    async def delete_grant(self, grant_id: uuid.UUID) -> bool:
        """Delete a grant."""
        grant = await self.get_grant_by_id(grant_id)
        if not grant:
            return False

        await self.db.delete(grant)
        logger.info("grant_deleted", grant_id=str(grant_id))
        return True

    async def get_grant_by_url(self, source_url: str) -> Optional[Grant]:
        """Find a grant by its source URL (for deduplication)."""
        result = await self.db.execute(
            select(Grant).where(Grant.source_url == source_url)
        )
        return result.scalar_one_or_none()

    async def upsert_grant(self, data: GrantCreate) -> tuple[Grant, bool]:
        """
        Insert or update a grant based on source_url.
        Returns (grant, is_new).
        """
        existing = await self.get_grant_by_url(data.source_url)

        if existing:
            update_data = GrantUpdate(**data.model_dump(exclude={"source_url", "source_name", "category_ids"}))
            updated = await self.update_grant(existing.id, update_data)
            return updated, False
        else:
            grant = await self.create_grant(data)
            return grant, True

    async def toggle_favorite(self, user_id: uuid.UUID, grant_id: uuid.UUID) -> bool:
        """Toggle a grant as favorite. Returns True if added, False if removed."""
        result = await self.db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.grant_id == grant_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            await self.db.delete(existing)
            return False
        else:
            fav = UserFavorite(user_id=user_id, grant_id=grant_id)
            self.db.add(fav)
            return True

    async def get_user_favorites(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> GrantListResponse:
        """Get user's favorite grants."""
        query = (
            select(Grant)
            .options(selectinload(Grant.categories))
            .join(UserFavorite, UserFavorite.grant_id == Grant.id)
            .where(UserFavorite.user_id == user_id)
            .order_by(desc(UserFavorite.created_at))
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        result = await self.db.execute(query)
        grants = result.scalars().unique().all()

        return GrantListResponse(
            items=[GrantResponse.model_validate(g) for g in grants],
            total=total,
            page=page,
            per_page=per_page,
            pages=math.ceil(total / per_page) if total > 0 else 0,
        )

    async def get_categories(self) -> list[Category]:
        """Get all categories."""
        result = await self.db.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def get_sources(self) -> list[str]:
        """Get distinct source names."""
        result = await self.db.execute(
            select(Grant.source_name).distinct().order_by(Grant.source_name)
        )
        return [row[0] for row in result.all()]

    async def get_stats(self) -> dict:
        """Get database statistics."""
        total = await self.db.execute(select(func.count(Grant.id)))
        active = await self.db.execute(
            select(func.count(Grant.id)).where(Grant.status == "active")
        )
        sources = await self.db.execute(
            select(func.count(func.distinct(Grant.source_name)))
        )

        return {
            "total_grants": total.scalar(),
            "active_grants": active.scalar(),
            "total_sources": sources.scalar(),
        }

    async def _update_search_vector(self, grant: Grant):
        """Update the full-text search vector for a grant."""
        try:
            await self.db.execute(
                text("""
                    UPDATE grants 
                    SET search_vector = to_tsvector('english', 
                        coalesce(title, '') || ' ' || 
                        coalesce(description, '') || ' ' || 
                        coalesce(eligibility, '') || ' ' ||
                        coalesce(country, '') || ' ' ||
                        coalesce(region, '')
                    )
                    WHERE id = :grant_id
                """),
                {"grant_id": grant.id}
            )
        except Exception as e:
            logger.warning("search_vector_update_failed", error=str(e))
