from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions as func

from models.base import ModelBase


class QuestionFile(ModelBase):
    __tablename__ = "question_files"

    id: int = Column(Integer, primary_key=True, index=True)
    conversation_id: int = Column(
        Integer, ForeignKey('conversations.id'), index=True, nullable=False
    )
    question_id: int = Column(Integer, ForeignKey('questions.id'), index=True, nullable=False)
    url: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    size: int = Column(Integer, nullable=False)
    extension: str = Column(String, nullable=False)
    content: str = Column(Text, nullable=False)
    type: str = Column(String, nullable=False)
    is_private: bool = Column(Boolean, nullable=False)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    conversation = relationship("Conversation", back_populates="question_files")
    question = relationship("Question", back_populates="question_files")
