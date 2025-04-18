from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from decouple import config

DB_URL = config("DB_URL")

async_engine = create_async_engine(DB_URL, echo=True, future=True)
async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
)
async def db_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session