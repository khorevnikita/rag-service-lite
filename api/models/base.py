from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, Integer, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Пивот-таблицы
document_keyword = Table(
    'document_keyword',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('keyword_id', Integer, ForeignKey('keywords.id'), primary_key=True),
)

document_model = Table(
    'document_model',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('model_id', Integer, ForeignKey('models.id'), primary_key=True),
)

paragraph_question = Table(
    'paragraph_question',
    Base.metadata,
    Column('paragraph_id', Integer, ForeignKey('paragraphs.id'), primary_key=True),
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('score', Float, nullable=True),
)


# Если вам нужен базовый класс для моделей, используйте Base
class ModelBase(Base):
    __abstract__ = True  # Указывает, что ModelBase является абстрактным классом
