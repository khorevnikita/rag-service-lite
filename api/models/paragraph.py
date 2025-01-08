from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import List, Optional

from elasticsearch import Elasticsearch
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Session, relationship

from config import es as es_config
from models.base import ModelBase, paragraph_question
from services import ai as ai_service
from services import s3


# Определение перечисления для статусов
class StatusEnum(Enum):
    QUEUED = "queued"
    INDEXING = "indexing"
    COMPLETED = "completed"


class Paragraph(ModelBase):
    __tablename__ = "paragraphs"

    id: int = Column(Integer, primary_key=True, index=True)
    document_id: int = Column(Integer, ForeignKey('documents.id'), index=True, nullable=False)
    status: StatusEnum = Column(
        SQLAlchemyEnum(StatusEnum), default=StatusEnum.QUEUED, nullable=False
    )
    content_url: Optional[str] = Column(String, nullable=True)
    content_length: Optional[int] = Column(Integer, nullable=True)
    embedding_url: Optional[str] = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=func.now())
    embedded_at: Optional[datetime] = Column(DateTime, nullable=True)
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    document = relationship("Document", back_populates="paragraphs")
    questions = relationship(
        "Question",
        secondary=paragraph_question,
        back_populates="paragraphs",
        cascade="all, delete",
    )

    async def make_embedding(self, db: Session) -> List[float] | List[int] | None:
        if not self.content_url:
            return None

        from models.document import Document
        from models.usage_logs import UsageLog

        document = db.get(Document, self.document_id)
        if not document:
            return None

        content = s3.read_content(self.content_url)

        ai_client = ai_service.AIService('openai', document.account_id)
        vector, usage_tokens = await ai_client.embed(content)
        UsageLog.log(
            db,
            {
                "account_id": document.account_id,
                "source_key": "paragraph",
                "source_id": self.id,
                "operation": "embedding",
                "embedding": usage_tokens.output_tokens,
            },
            usage_tokens.model_name,
        )

        remote_path = f'documents/{document.id}/paragraphs/{self.id}/vector.json'
        s3.put_object(remote_path, json.dumps(vector))
        self.embedding_url = remote_path
        self.embedded_at = datetime.now()
        db.commit()
        return vector

    def save_to_es(self, db: Session, vector: List[float] | List[int], content: str) -> None:
        from models.document import Document

        es = Elasticsearch([es_config.host])
        document = db.get(Document, self.document_id)
        if not document:
            return

        es_doc = {
            'account_id': document.account_id,
            'document_id': self.document_id,
            'content_vector': vector,
            'text': content,
        }
        es.index(index=es_config.index, id=str(self.id), body=es_doc)
