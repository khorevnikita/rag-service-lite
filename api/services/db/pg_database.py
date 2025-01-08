import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Синхронный движок и фабрика сессий
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables")

engine = create_engine(f'postgresql://{DATABASE_URL}')
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Асинхронный движок и фабрика сессий
async_engine: AsyncEngine = create_async_engine(f'postgresql+asyncpg://{DATABASE_URL}', echo=False)

AsyncSessionLocal = sessionmaker(  # type: ignore
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


# Зависимость для получения асинхронной сессии базы данных
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
