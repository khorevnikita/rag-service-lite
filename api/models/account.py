from __future__ import annotations

import uuid
from datetime import datetime

import bcrypt
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import functions as func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import ModelBase


class Account(ModelBase):
    __tablename__ = "accounts"

    id: int = Column(Integer, primary_key=True, index=True)
    login: str = Column(String, nullable=True)
    _password: str = Column(String, name="password", nullable=False)
    supertokens_id: uuid.UUID = Column(UUID, nullable=True)
    is_active: bool = Column(Boolean, nullable=False, default=False)
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())
    documents = relationship("Document", back_populates="account")
    questions = relationship("Question", back_populates="account")
    usage_logs = relationship("UsageLog", back_populates="account")
    settings = relationship("Settings", back_populates="account")
    keywords = relationship("Keyword", back_populates="account")
    conversations = relationship("Conversation", back_populates="account")

    def set_password(self, password: str):
        self._password = bcrypt.hashpw(str(password).encode('utf-8'), bcrypt.gensalt()).decode(
            'utf-8'
        )

    def check_password(self, password) -> bool:
        return bcrypt.checkpw(str(password).encode('utf-8'), self._password.encode('utf-8'))
