from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import functions as func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from models.base import ModelBase


class Conversation(ModelBase):
    __tablename__ = "conversations"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=True)
    name: Optional[str] = Column(String, nullable=True)
    meta: Optional[str] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    account = relationship("Account", back_populates="conversations")
    questions = relationship("Question", back_populates="conversation")
    question_files = relationship("QuestionFile", back_populates="conversation")

    @staticmethod
    async def find_or_create(db: AsyncSession, account_id, conversation_id=None, name=""):
        conversation = None

        # Асинхронно ищем существующий объект Conversation
        if conversation_id:
            conversation_query = select(Conversation).where(
                (Conversation.id == conversation_id) & (Conversation.account_id == account_id)
            )
            result = await db.execute(conversation_query)
            conversation = result.scalars().first()

        if not conversation:
            conversation = Conversation(account_id=account_id, name=f'{name[:100]}')
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        return conversation
