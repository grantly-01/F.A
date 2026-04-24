"""
Funding Aggregator - Auth Service
"""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication and user management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if user exists
        existing = await self.db.execute(
            select(User).where(
                (User.email == user_data.email) | (User.username == user_data.username)
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("User with this email or username already exists")

        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        logger.info("user_registered", user_id=str(user.id), username=user.username)
        return user

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning("auth_failed", username=username)
            return None

        if not user.is_active:
            logger.warning("inactive_user_login", username=username)
            return None

        logger.info("user_authenticated", user_id=str(user.id))
        return user

    async def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        return result.scalar_one_or_none()

    async def refresh_tokens(self, refresh_token: str) -> Optional[Token]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user = await self.get_user_by_id(payload["sub"])
        if not user or not user.is_active:
            return None

        return await self.create_tokens(user)
