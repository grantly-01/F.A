"""
Funding Aggregator - User Schemas (Pydantic)
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    preferences: Optional[dict] = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    preferences: Optional[dict] = None
    favorites_count: int = 0
