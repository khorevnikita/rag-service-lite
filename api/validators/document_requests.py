from typing import List, Optional

from pydantic import BaseModel, Field, validator


# Создайте Pydantic модель для вашего запроса
class CreateDocumentRequest(BaseModel):
    url: str
    name: str
    keywords: List[str] = Field(default_factory=list)
    meta: Optional[str] = None

    @validator('keywords')
    def check_keywords_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Keywords must contain at least one item')
        return v


class UpdateDocumentRequest(BaseModel):
    name: str


class DocumentSearchRequest(BaseModel):
    query: str
