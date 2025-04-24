from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from pydantic import TypeAdapter
from app.db.db import db_session
from app.deps.pagination import pagination_params
from app.db.models import Film
from sqlmodel import select
from app.enums import Role
from app.api.auth.deps import require_role
from uuid import UUID

from .service import create_film, get_film_by_id, get_all_film, search_film_by_title
from .schemas import FilmCreate, FilmSummary, FilmDetail

router = APIRouter(prefix="/films", tags=["Films"])
@router.get(
    "/search",
    response_model=list[FilmSummary],
    responses={
        200: {"description": "Films retrieved successfully"},
        404: {"description": "No films found"},
    },
)
async def search_films(
    title: str,
    session: AsyncSession = Depends(db_session),
    pagination: dict = Depends(pagination_params)
):
    films = await search_film_by_title(title, pagination, session)
    if not films:
        raise HTTPException(status_code=404, detail="No films found")
        
    return films
@router.post(
    "",
    status_code=201,
    response_model=None,
    dependencies=[Depends(require_role(Role.ADMIN))],
    responses={
        201: {"description": "Film created successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def add_new_film(
    film: Annotated[str, Form()], images: list[UploadFile],
    session: AsyncSession = Depends(db_session),
    _: str = Depends(require_role(Role.ADMIN))
):
    try:
        film_data = TypeAdapter(FilmCreate).validate_json(film)
        
        await create_film(film_data, images, session)
        return {"message": "Film created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "",
    response_model=list[FilmSummary],
    responses={
        200: {"description": "Films retrieved successfully"},
        404: {"description": "No films found"},
    },
)
async def get_film_list(
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session)
):
    films = await get_all_film(pagination, session)
    if not films:
        raise HTTPException(status_code=404, detail="No films found")
        
    return films

@router.get(
    "/{film_id}",
    response_model=FilmDetail,
    responses={
        200: {"description": "Film retrieved successfully"},
        404: {"description": "Film not found"},
    },
)    
async def get_film_details(
    film_id: UUID,
    session: AsyncSession = Depends(db_session),
):

    film = await get_film_by_id(film_id, session)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    
    return film

