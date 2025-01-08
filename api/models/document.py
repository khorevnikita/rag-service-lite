from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String, asc
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Mapped, Session, relationship

from config.ai import AI_PROVIDER
from models.base import ModelBase, document_keyword, paragraph_question
from models.keywords import Keyword
from models.paragraph import Paragraph
from models.usage_logs import UsageLog
from services import s3
from services.ai import AIService
from services.kafka import producer


# Определение перечисления для статусов
class StatusEnum(Enum):
    QUEUED = "queued"
    READING = "reading"
    SLICED = "sliced"
    READ = "read"


class Document(ModelBase):
    __tablename__ = "documents"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=False)
    url: str = Column(String, nullable=False)
    status: StatusEnum = Column(
        SQLAlchemyEnum(StatusEnum), default=StatusEnum.QUEUED, nullable=False
    )
    name: str = Column(String, nullable=True)
    content_length: Optional[int] = Column(Integer, nullable=True)
    content_url: Optional[str] = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=func.now())
    meta: Optional[str] = Column(String, nullable=True)
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    paragraphs = relationship("Paragraph", back_populates="document", cascade="all, delete-orphan")
    account = relationship("Account", back_populates="documents")
    questions = relationship("Question", secondary=paragraph_question, back_populates="documents")

    keywords: Mapped[List["Keyword"]] = relationship(
        "Keyword",
        secondary=document_keyword,  # связывающая таблица
        back_populates="documents",
    )

    # Метод для отправки сообщения в Kafka
    def send_to_reader(self) -> None:
        message = {'id': self.id, 'status': self.status.value, 'url': self.url}
        producer.send_message('api', 'document_created', f'document_{self.id}', message)

    def set_content(self, db: Session, content: str) -> None:
        document_content_url = f'documents/{self.id}/content.txt'
        s3.put_object(remote_path=document_content_url, content=content)
        self.content_url = document_content_url
        self.content_length = len(content)
        db.commit()
        db.refresh(self)

    async def set_meta(self, db: Session) -> None:
        paragraphs = (
            db.query(Paragraph)
            .filter(Paragraph.document_id == self.id, Paragraph.content_url.isnot(None))
            .order_by(asc(Paragraph.id))
            .limit(2)
            .all()
        )

        try:
            start_content = "\n".join(
                [s3.read_content(p.content_url) for p in paragraphs if p.content_url]
            )

            ai_client = AIService(AI_PROVIDER, self.account_id)
            meta, usage = await ai_client.extract_meta_from_text(start_content)

            self.meta = meta
            db.commit()
            db.refresh(self)

            UsageLog.log(
                db,
                {
                    "account_id": self.account_id,
                    "source_key": "document",
                    "source_id": self.id,
                    "operation": "extract_meta",
                    "input": usage.input_tokens,
                    "output": usage.output_tokens,
                },
                usage.model_name,
            )
        except Exception as e:
            logging.error(f"ERROR WHILE GETTING CONTENT: {e}")
            return

    def create_paragraphs(self, db: Session, blocks: List[str]) -> None:
        i = 0
        for block in blocks:
            content_url = f'documents/{self.id}/paragraphs/{i}.txt'
            paragraph = Paragraph(
                document_id=self.id,
                content_url=content_url,
                content_length=len(block),
            )
            db.add(paragraph)
            db.commit()
            db.refresh(paragraph)
            s3.put_object(remote_path=content_url, content=block)
            producer.send_message(
                'consumer',
                'paragraph_created',
                f'paragraph_{paragraph.id}',
                {'id': paragraph.id, 'url': content_url},
            )

            i = i + 1

        self.status = StatusEnum.SLICED
        db.commit()
