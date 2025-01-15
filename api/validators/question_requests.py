from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from models.question import AnswerFormat


# Определите модель для элемента файла.
class FileItem(BaseModel):
    file_path: str
    filename: str
    size: int
    extension: str


# Модель для свойства параметра
class SchemaProperty(BaseModel):
    type: Literal["string", "number", "boolean", "object", "array"] = Field(
        ..., description="Тип параметра"
    )
    description: str = Field(..., description="Описание параметра")
    enum: Optional[List[Any]] = Field(None, description="Допустимые значения параметра")
    items: Optional[Dict[str, Any]] = Field(
        None, description="Тип значений в массиве"
    )  # todo: обязательно, если type ="array"

    def to_dict(self) -> Dict[str, Any]:
        # Исключаем поля, значение которых равно None
        return {k: v for k, v in self.dict().items() if v is not None}


# Модель для input_schema или parameters
class SchemaInput(BaseModel):
    type: Literal["object"] = Field("object", description="Тип схемы, должен быть 'object'")
    properties: Dict[str, SchemaProperty] = Field(..., description="Свойства входных параметров")
    required: Optional[List[str]] = Field(default=[], description="Список обязательных параметров")
    additionalProperties: Optional[bool] = Field(
        False, description="Разрешены ли дополнительные свойства"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "properties": {k: v.to_dict() for k, v in self.properties.items()},
            "required": self.required,
            "additionalProperties": self.additionalProperties,
        }


# Модель для функции
class FunctionDefinition(BaseModel):
    name: str = Field(..., description="Имя функции")
    description: str = Field(..., description="Описание функции")
    input_schema: SchemaInput = Field(..., description="Схема входных данных для функции")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.input_schema.to_dict(),
        }


class CreateQuestionRequest(BaseModel):
    text: Optional[str] = ""
    webhook: Optional[str] = ""
    context: Optional[str] = ""
    conversation_id: Optional[int] = None
    stream: bool = False
    files: Optional[List[FileItem]] = None
    tools: Optional[List[FunctionDefinition]] = None
    answer_format: Optional[AnswerFormat] = AnswerFormat.TEXT

    @model_validator(mode="after")
    def check_text_media_or_files(self) -> "CreateQuestionRequest":
        # В Pydantic v2 после валидации доступна уже сама модель через self
        if not self.text and not self.files:
            raise ValueError('At least one of text, media, or files must be provided.')
        return self
