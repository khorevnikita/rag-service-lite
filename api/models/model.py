from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, insert
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import relationship

from models.base import ModelBase, document_model


class Model(ModelBase):
    __tablename__ = "models"

    id: int = Column(Integer, primary_key=True, index=True)
    base_model_name: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    input: float = Column(Float, nullable=False)
    output: float = Column(Float, nullable=False)
    questions = relationship("Question", back_populates="model")

    def attach_documents(self, db, docs_id):
        for doc_id in docs_id:
            # Создаем запись в пивот-таблице
            insert_stmt = insert(document_model).values(document_id=doc_id, model_id=self.id)
            db.execute(insert_stmt)
        db.commit()

    def calculate_price(self, log) -> float:
        price = 0.0
        if log.input_usage:
            if self.base_model_name == "whisper-1":
                # Звуковая - кол-во секунд на цену за минуту
                price = price + log.input_usage * self.input / 60
            else:
                price = price + log.input_usage * self.input / 1000000
        if log.output_usage:
            price = price + log.output_usage * self.output / 1000000
        if log.embedding_usage:
            price = price + log.embedding_usage * self.input / 1000000
        return price
