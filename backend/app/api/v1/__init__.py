"""Funding Aggregator - API v1 Package"""
from fastapi import APIRouter
from app.api.v1 import grants, auth, users, ai

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(grants.router, prefix="/grants", tags=["Grants"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(ai.router, prefix="/ai", tags=["AI"])
