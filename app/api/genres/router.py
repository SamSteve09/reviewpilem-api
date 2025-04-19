from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.auth.deps import require_role
from app.db.models import Genre
from .service import create_genre, get_all_genres, update_genre_by_id
from .schemas import CreateGenre
from app.enums import Role

from app.api.response_code import common_responses

router = APIRouter(prefix="/genres", tags=["Genres"])

@router.post("", response_model = Genre, status_code=201, responses=common_responses)
async def add_new_genre(
    request: CreateGenre,
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        return await create_genre(request, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[Genre])
async def get_genres(
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        return await get_all_genres(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{genre_id}", response_model=Genre, responses=common_responses)
async def update_genre(
    genre_id: int,
    request: CreateGenre,
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        genre = Genre(id=genre_id, genre_name=request.genre_name)
        return await update_genre_by_id(genre, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))