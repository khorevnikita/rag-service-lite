from typing import List

from pydantic import BaseModel


# Создайте Pydantic модель для вашего запроса
class CreateModelRequest(BaseModel):
    base_model_name: str
    documents_id: List[int]
