from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.auth.deps import require_role
from app.db.models import Genre
from .service import create_genre, get_all_genres, update_genre_by_id
from .schemas import CreateGenre
from app.enums import Role
from app.exceptions import UniqueConstraintViolation

from app.api.response_code import common_responses

router = APIRouter(prefix="/genres", tags=["Genres"])

@router.post("", response_model = Genre, status_code=201, 
responses={409: {
            **common_responses[409],
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Genre with name {genre_name} already exists"
                    }
                }
            }
        }, 401: {**common_responses[401]}, 403 : {**common_responses[403]}, 500: {**common_responses[500]}})
async def add_new_genre(
    request: CreateGenre,
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        return await create_genre(request, session)
    except UniqueConstraintViolation as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("", response_model=list[Genre], responses={500: {**common_responses[500]}})
async def get_genres(
    session: AsyncSession = Depends(db_session)
):
    try:
        return await get_all_genres(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{genre_id}", response_model=Genre,
                responses={404: {**common_responses[404], "content": {
                    "application/json": {
                        "example": {
                            "detail": "Genre with id {genre_id} does not exist"
                        }
                    }}},
                    409: {**common_responses[409], "content": {
                        "application/json": {
                            "example": {
                                "detail": "Genre name {genre_name} is already used."
                            }
                    }}},
                    401: {**common_responses[401]}, 
                    403 : {**common_responses[403]},
                    500: {**common_responses[500]}})
async def update_genre(
    genre_id: int,
    request: CreateGenre,
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        genre = Genre(id=genre_id, genre_name=request.genre_name)
        return await update_genre_by_id(genre, session)
    except UniqueConstraintViolation as e:
        raise HTTPException(status_code=400, detail=str(e))