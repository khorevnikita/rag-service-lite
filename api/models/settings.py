from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum, func
from sqlalchemy import ForeignKey, Integer, String, Text, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions

import config.ai
from config.ai import OPENAI_API_KEY
from models.base import ModelBase
from services.db.pg_database import SessionLocal


class SettingsKey(Enum):
    OPENAI_API_KEY = "openai_api_key"
    ACCOUNT_API_KEY = "account_api_key"
    DEFAULT_CONTEXT = "default_context"
    PROMPT_TEMPLATE = "prompt_template"
    GENERATIVE_PROVIDER = "generative_provider"
    GENERATIVE_MODEL = "generative_model"
    EMBEDDING_MODEL = "embedding_model"
    TEMPERATURE = "temperature"


def get_openai_key(account_id: int) -> str:
    api_key = OPENAI_API_KEY
    with SessionLocal() as db:
        settings = (
            db.query(Settings)
            .filter(
                Settings.key == SettingsKey.OPENAI_API_KEY,
                Settings.account_id == account_id,
            )
            .first()
        )
        if settings and settings.value:
            api_key = settings.value

    return api_key or ""


async def get_context_template(db: AsyncSession, account_id: int) -> str:
    # Инициализируем контекст пустой строкой
    context = ""

    # Создаем запрос с использованием select()
    settings_query = select(Settings).where(
        (func.lower(cast(Settings.key, String)) == SettingsKey.DEFAULT_CONTEXT.value)
        & (Settings.account_id == account_id)
    )

    # Выполняем запрос асинхронно
    result = await db.execute(settings_query)

    # Получаем первый результат из полученных данных
    settings = result.scalars().first()

    # Если настройки найдены, обновляем контекст
    if settings:
        context = settings.value

    return context


async def get_prompt_template(db: AsyncSession, account_id: int) -> str:
    template = "{{prompt}}"
    settings_query = select(Settings).where(
        (func.lower(cast(Settings.key, String)) == SettingsKey.PROMPT_TEMPLATE.value)
        & (Settings.account_id == account_id)
    )

    result = await db.execute(settings_query)
    settings = result.scalars().first()
    if settings:
        template = settings.value

    return template


def get_generative_provider(account_id: int) -> str:
    provider = config.ai.AI_PROVIDER
    with SessionLocal() as db:
        settings = (
            db.query(Settings)
            .filter(
                Settings.key == SettingsKey.GENERATIVE_PROVIDER,
                Settings.account_id == account_id,
            )
            .first()
        )
        if settings:
            provider = settings.value
    print("GENERATIVE PROVIDER", provider)
    return provider


def get_generative_model(account_id: int) -> str:
    model = config.ai.AI_DEFAULT_MODEL
    with SessionLocal() as db:
        settings = (
            db.query(Settings)
            .filter(
                Settings.key == SettingsKey.GENERATIVE_MODEL,
                Settings.account_id == account_id,
            )
            .first()
        )
        if settings:
            model = settings.value
    print("GENERATIVE MODEL", model)
    return model


def get_embedding_model(account_id: int) -> str:
    model = "voyage-large-2-instruct"
    with SessionLocal() as db:
        settings = (
            db.query(Settings)
            .filter(
                Settings.key == SettingsKey.EMBEDDING_MODEL,
                Settings.account_id == account_id,
            )
            .first()
        )
        if settings:
            model = settings.value
    print("EMBEDDING MODEL", model)
    return model


def get_temperature(account_id: int) -> float:
    temperature = 0.1
    with SessionLocal() as db:
        settings = (
            db.query(Settings)
            .filter(
                Settings.key == SettingsKey.TEMPERATURE,
                Settings.account_id == account_id,
            )
            .first()
        )
        if settings:
            t = float(settings.value)
            if t:
                temperature = t
    print("Temperature", temperature)
    return temperature


class Settings(ModelBase):
    __tablename__ = "settings"

    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=True)
    key: SettingsKey = Column(SQLAlchemyEnum(SettingsKey), nullable=True)
    value: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, server_default=functions.now())
    updated_at: datetime = Column(DateTime, server_default=functions.now(), onupdate=functions.now())
    account = relationship("Account", back_populates="settings")

    def generate_api_key(self) -> None:
        # Генерация безопасного случайного числа
        random_bytes = secrets.token_bytes(32)  # 32 байта случайных данных
        # Преобразование в безопасный хеш (например, SHA256)
        self.value = hashlib.sha256(random_bytes).hexdigest()
