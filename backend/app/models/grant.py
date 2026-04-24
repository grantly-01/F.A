"""
Funding Aggregator - Grant Models
"""
import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    Column, String, Text, DateTime, Date, Numeric, Boolean,
    ForeignKey, Index, Table, JSON, Enum as SAEnum, func
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class Category(Base):
    """Grant category model."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#8b5cf6")  # HEX color

    # Relationships
    grants = relationship("Grant", secondary="grant_categories", back_populates="categories")

    def __repr__(self) -> str:
        return f"<Category(name='{self.name}')>"


class GrantCategory(Base):
    """Association table for Grant-Category many-to-many relationship."""
    __tablename__ = "grant_categories"

    grant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grants.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )


class Grant(Base):
    """Grant/funding opportunity model."""
    __tablename__ = "grants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_ai: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI-generated summary
    source_url: Mapped[str] = mapped_column(String(2000), unique=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Funding details
    amount_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    amount_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Dates & Deadlines
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Details
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords_ai: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # AI-extracted keywords
    
    # Location
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="active", index=True
    )  # active, expired, closed

    # Full-text search vector
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    # Timestamps
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    categories = relationship("Category", secondary="grant_categories", back_populates="grants")
    favorited_by = relationship("UserFavorite", back_populates="grant", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_grants_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_grants_deadline_status", "deadline", "status"),
        Index("ix_grants_amount", "amount_min", "amount_max"),
    )

    def __repr__(self) -> str:
        return f"<Grant(title='{self.title[:50]}...')>"
