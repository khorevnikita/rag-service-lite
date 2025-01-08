from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import relationship

from models.base import ModelBase, document_keyword


class Keyword(ModelBase):
    __tablename__ = "keywords"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=False)
    text: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    account = relationship("Account", back_populates="keywords")
    documents = relationship("Document", secondary=document_keyword, back_populates="keywords")
