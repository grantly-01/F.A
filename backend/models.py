from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, Date
from sqlalchemy.sql import func
from backend.database import Base


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    funder = Column(String(200))
    amount_min = Column(BigInteger)
    amount_max = Column(BigInteger)
    currency = Column(String(10), default="KZT")
    deadline = Column(Date)
    eligibility = Column(Text)
    source_url = Column(String(500))
    source_raw = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())