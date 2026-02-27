from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import date

from database import engine, Base, get_db
from models import Grant
from schemas import GrantCreate, GrantResponse, GrantSearch
from auth import create_access_token, verify_token
from collector import collect_from_url, TEST_URLS

# Создаем таблицы
Base.metadata.create_all(bind=engine)

backend = FastAPI(
    title="Funding Aggregator - Kazakhstan",
    description="Агрегатор грантов и финансирования для Казахстана с AI-обработкой",
    version="1.0.0"
)

backend.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@backend.get("/")
def root():
    return {
        "service": "Funding Aggregator Kazakhstan",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "grants": "/grants",
            "search": "/grants/search",
            "collect": "/collect",
            "stats": "/stats"
        }
    }


@backend.get("/grants", response_model=List[GrantResponse])
def get_grants(
        skip: int = 0,
        limit: int = 100,
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        funder: Optional[str] = None,
        status: str = "active",
        search: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Получить список грантов с фильтрами"""
    query = db.query(Grant).filter(Grant.status == status)

    if min_amount:
        query = query.filter(Grant.amount_max >= min_amount)
    if max_amount:
        query = query.filter(Grant.amount_min <= max_amount)
    if funder:
        query = query.filter(Grant.funder.contains(funder))
    if search:
        query = query.filter(
            or_(
                Grant.title.contains(search),
                Grant.description.contains(search),
                Grant.eligibility.contains(search)
            )
        )

    return query.order_by(Grant.deadline).offset(skip).limit(limit).all()


@backend.post("/grants/search", response_model=List[GrantResponse])
def search_grants(search_params: GrantSearch, db: Session = Depends(get_db)):
    """Поиск грантов по параметрам"""
    query = db.query(Grant)

    if search_params.query:
        q = f"%{search_params.query}%"
        query = query.filter(
            or_(Grant.title.ilike(q), Grant.description.ilike(q))
        )
    if search_params.min_amount:
        query = query.filter(Grant.amount_max >= search_params.min_amount)
    if search_params.max_amount:
        query = query.filter(Grant.amount_min <= search_params.max_amount)
    if search_params.funder:
        query = query.filter(Grant.funder.contains(search_params.funder))
    if search_params.deadline_after:
        query = query.filter(Grant.deadline >= search_params.deadline_after)

    return query.all()


@backend.post("/collect", status_code=status.HTTP_201_CREATED)
def trigger_collection(
        url: Optional[str] = None,
        username: str = Depends(verify_token),
        db: Session = Depends(get_db)
):
    """Запустить сбор данных (требует JWT)"""

    if url:
        success = collect_from_url(db, url)
        if success:
            return {"message": "Grant collected successfully", "url": url}
        raise HTTPException(status_code=400, detail="Failed to collect from URL")

    # Если URL не указан, используем тестовые
    results = []
    for test_url in TEST_URLS[:2]:  # Первые 2 для демо
        success = collect_from_url(db, test_url)
        results.append({"url": test_url, "success": success})
    return {"message": "Batch collection completed", "results": results}


@backend.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Статистика по грантам"""
    total = db.query(Grant).count()
    active = db.query(Grant).filter(Grant.status == "active").count()

    funders = db.query(Grant.funder, func.count(Grant.id)).group_by(Grant.funder).all()
    total_amount = db.query(func.sum(Grant.amount_max)).scalar() or 0

    return {
        "total_grants": total,
        "active_grants": active,
        "funders": [{"name": f[0], "count": f[1]} for f in funders],
        "total_max_amount": int(total_amount)
    }


@backend.post("/login")
def login():
    """Получить JWT токен (упрощенно)"""
    token = create_access_token(data={"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@backend.get("/health")
def health_check():
    return {"status": "healthy"}