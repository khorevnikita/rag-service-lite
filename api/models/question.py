from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String, Text, insert
from sqlalchemy.sql import functions as func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship

from models.base import ModelBase, paragraph_question
from models.question_file import QuestionFile


class ModeEnum(Enum):
    CONTEXT = "context"


class Question(ModelBase):
    __tablename__ = "questions"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=True)
    conversation_id: int = Column(
        Integer, ForeignKey('conversations.id'), index=True, nullable=True
    )
    model_id: Optional[int] = Column(Integer, ForeignKey('models.id'), nullable=True)
    text: Optional[str] = Column(Text, nullable=False)
    answer: Optional[str] = Column(Text, nullable=True)
    reaction: Optional[str] = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    answered_at: Optional[datetime] = Column(DateTime, nullable=True)
    reacted_at: Optional[datetime] = Column(DateTime, nullable=True)
    available_tools: Optional[Any] = Column(JSON, default=False, nullable=True)
    called_tools: Optional[Any] = Column(JSON, default=False, nullable=True)
    model = relationship("Model", back_populates="questions")
    account = relationship("Account", back_populates="questions")
    conversation = relationship("Conversation", back_populates="questions")
    paragraphs = relationship("Paragraph", secondary=paragraph_question, back_populates="questions")
    documents = relationship("Document", secondary=paragraph_question, back_populates="questions")
    question_files: Mapped[List["QuestionFile"]] = relationship(
        "QuestionFile", back_populates="question"
    )

    async def attach_paragraphs(self, db: AsyncSession, paragraphs, scores):
        # Собираем данные для массовой вставки
        insert_data = [
            {
                'paragraph_id': paragraph.id,
                'document_id': paragraph.document_id,
                'question_id': self.id,
                'score': scores[i],
            }
            for i, paragraph in enumerate(paragraphs)
        ]

        # Выполняем массовую вставку одним запросом
        await db.execute(insert(paragraph_question).values(insert_data))
        await db.commit()

        return True
