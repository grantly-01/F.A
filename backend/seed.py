from datetime import date
from sqlalchemy.orm import Session

from .models import Grant


DEMO_GRANTS = [
    {
        "title": "Гранты для IT‑стартапов (демо)",
        "description": "Демо-запись для проекта. Поддержка ранних стартапов: менторство, трекшн, пилоты, грантовое финансирование.",
        "funder": "QazTech (демо)",
        "amount_min": 1_000_000,
        "amount_max": 10_000_000,
        "currency": "KZT",
        "deadline": date(2026, 4, 15),
        "eligibility": "Стартапы, зарегистрированные в РК; MVP; команда 2+ человека.",
        "source_url": "https://example.com/demo-it",
        "status": "active",
        "category": "grant",
        "country": "KZ",
    },
    {
        "title": "Субсидии на экспорт (демо)",
        "description": "Компенсация части затрат на участие в международных выставках и продвижение продукции.",
        "funder": "QazTrade (демо)",
        "amount_min": 500_000,
        "amount_max": 20_000_000,
        "currency": "KZT",
        "deadline": date(2026, 6, 1),
        "eligibility": "МСП РК, наличие экспортных контрактов или планов выхода на рынок.",
        "source_url": "https://example.com/demo-export",
        "status": "active",
        "category": "subsidy",
        "country": "KZ",
    },
    {
        "title": "Стипендия на обучение (демо)",
        "description": "Поддержка студентов и молодых исследователей: обучение, стажировки, исследовательские проекты.",
        "funder": "Bolashak (демо)",
        "amount_min": None,
        "amount_max": None,
        "currency": "KZT",
        "deadline": date(2026, 5, 10),
        "eligibility": "Граждане РК, конкурсный отбор, мотивационное письмо.",
        "source_url": "https://example.com/demo-scholarship",
        "status": "active",
        "category": "scholarship",
        "country": "KZ",
    },
]


def seed_if_empty(db: Session) -> None:
    has_any = db.query(Grant.id).limit(1).first() is not None
    if has_any:
        return

    for item in DEMO_GRANTS:
        db.add(Grant(**item))
    db.commit()

