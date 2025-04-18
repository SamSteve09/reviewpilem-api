from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from app.db.db import db_session
from app.db.models import Genre

async def create_genre(genre: Genre, session: AsyncSession = Depends(db_session)) -> Genre:
    result = await session.exec(select(Genre).where(Genre.genre_name == genre.genre_name))
    existing = result.first()
    if existing:
        raise ValueError(f"Genre with name {genre.genre_name} already exists")

    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre

async def get_genre_by_id(genre_id: int, session: AsyncSession = Depends(db_session)) -> Genre:
    result = await session.exec(select(Genre).where(Genre.id == genre_id))
    genre = result.first()
    if not genre:
        raise ValueError(f"Genre with id {genre_id} does not exist")
    return genre

async def get_all_genres(session: AsyncSession = Depends(db_session)) -> list[Genre]:
    result = await session.exec(select(Genre))
    genres = result.all()
    return genres

async def update_genre_by_id(genre: Genre, session: AsyncSession = Depends(db_session)) -> Genre:
    existing_genre = await session.get(Genre, genre.id)
    if not existing_genre:
        raise ValueError(f"Genre with id {genre.id} does not exist")
    
    result = await session.exec(
        select(Genre).where(Genre.genre_name == genre.genre_name, Genre.id != genre.id)
    )
    conflict = result.first()
    if conflict:
        raise ValueError(f"Genre name '{genre.genre_name}' is already used.")
    existing_genre.genre_name = genre.genre_name
    await session.commit()
    await session.refresh(existing_genre)
    return existing_genre

