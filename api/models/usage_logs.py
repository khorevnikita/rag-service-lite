from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions as func

from models.base import ModelBase
from models.model import Model


class UsageLog(ModelBase):
    __tablename__ = "usage_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=True)
    source_key: str = Column(String, nullable=False)
    source_id: int = Column(Integer, nullable=False)
    operation: str = Column(String, nullable=False)
    input_usage: int = Column(Integer, nullable=False, default=0)
    output_usage: int = Column(Integer, nullable=False, default=0)
    embedding_usage: int = Column(Integer, nullable=False, default=0)
    price: float = Column(Float, nullable=False, default=0)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    account = relationship("Account", back_populates="usage_logs")

    @staticmethod
    def log(db, data, model_name: str):
        m = UsageLog(
            account_id=data["account_id"],
            source_key=data["source_key"],
            source_id=data["source_id"],
            operation=data["operation"],
            input_usage=data.get("input", 0),
            output_usage=data.get("output", 0),
            embedding_usage=data.get("embedding", 0),
        )

        model = db.query(Model).filter(Model.base_model_name == model_name).first()
        m.price = model.calculate_price(m)

        db.add(m)
        db.commit()

        return True

    @staticmethod
    async def log_async(db: AsyncSession, data, model_name: str):
        m = UsageLog(
            account_id=data["account_id"],
            source_key=data["source_key"],
            source_id=data["source_id"],
            operation=data["operation"],
            input_usage=data.get("input", 0),
            output_usage=data.get("output", 0),
            embedding_usage=data.get("embedding", 0),
        )

        # Создаем асинхронный запрос с использованием select()
        model_query = select(Model).where(Model.base_model_name == model_name)
        result = await db.execute(model_query)
        model = result.scalars().first()
        if not model:
            return False
        m.price = model.calculate_price(m)

        db.add(m)
        await db.commit()

        return True
