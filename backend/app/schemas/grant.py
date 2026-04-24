"""
Funding Aggregator - Grant Schemas (Pydantic)
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#8b5cf6", max_length=7)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class GrantBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    source_url: str = Field(..., max_length=2000)
    source_name: str = Field(..., max_length=100)
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    currency: str = Field(default="USD", max_length=3)
    deadline: Optional[date] = None
    posted_date: Optional[date] = None
    eligibility: Optional[str] = None
    requirements: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    status: str = Field(default="active", max_length=20)


class GrantCreate(GrantBase):
    category_ids: list[int] = Field(default_factory=list)


class GrantUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    currency: Optional[str] = Field(None, max_length=3)
    deadline: Optional[date] = None
    eligibility: Optional[str] = None
    requirements: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    category_ids: Optional[list[int]] = None


class GrantResponse(GrantBase):
    id: uuid.UUID
    summary_ai: Optional[str] = None
    keywords_ai: Optional[dict] = None
    categories: list[CategoryResponse] = Field(default_factory=list)
    scraped_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GrantListResponse(BaseModel):
    """Paginated list of grants."""
    items: list[GrantResponse]
    total: int
    page: int
    per_page: int
    pages: int


class GrantSearchQuery(BaseModel):
    """Search and filter parameters."""
    q: Optional[str] = None  # Search query
    category: Optional[str] = None
    source: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = "active"
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    deadline_before: Optional[date] = None
    deadline_after: Optional[date] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class AISearchQuery(BaseModel):
    """Natural language search query powered by AI."""
    query: str = Field(..., min_length=3, max_length=500)
    max_results: int = Field(default=10, ge=1, le=50)
