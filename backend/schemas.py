from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class GrantBase(BaseModel):
    title: str
    description: Optional[str] = None
    funder: Optional[str] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    currency: str = "KZT"
    deadline: Optional[date] = None
    eligibility: Optional[str] = None
    status: str = "active"


class GrantCreate(GrantBase):
    source_url: Optional[str] = None


class GrantResponse(GrantBase):
    id: int
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GrantSearch(BaseModel):
    query: Optional[str] = None
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    funder: Optional[str] = None
    deadline_after: Optional[date] = None