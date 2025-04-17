from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from config import Settings

DB_URL = Settings().DB_URL

async_engine = create_async_engine(DB_URL, echo=True, future=True)

async def db_session() -> AsyncGenerator:
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session