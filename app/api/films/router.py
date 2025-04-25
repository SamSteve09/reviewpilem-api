from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from pydantic import TypeAdapter

from app.db.db import db_session
from app.api.response_code import common_responses
from app.deps.pagination import pagination_params
from app.enums import Role
from app.api.auth.deps import require_role
from uuid import UUID

from .service import create_film, get_film_by_id, get_all_film, search_film_by_title
from .schemas import FilmCreate, FilmSummary, FilmDetail

router = APIRouter(prefix="/films", tags=["Films"])
@router.get(
    "/search",
    response_model=list[FilmSummary],
    responses={500: {**common_responses[500]}})
async def search_films(
    title: str,
    session: AsyncSession = Depends(db_session),
    pagination: dict = Depends(pagination_params)
):
    films = await search_film_by_title(title, pagination, session)        
    return films
@router.post(
    "",
    status_code=201,
    response_model=None,
    dependencies=[Depends(require_role(Role.ADMIN))],
    responses={
        400: {**common_responses[400], "content": {
            "application/json": {
                "example": {
                    "detail": "Genre '{genre_name}' does not exist"
                }
            }
        }},
        401: {**common_responses[401]},
        403: {**common_responses[403]},
        500: {**common_responses[500]}
    }
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
        500: {**common_responses[500]}
    },
)
async def get_film_list(
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session)
):
    films = await get_all_film(pagination, session)
        
    return films

@router.get(
    "/{film_id}",
    response_model=FilmDetail,
    responses={
        404: {**common_responses[404], "content": {
            "application/json": {
                "example": {
                    "detail": "Film with id {film_id} does not exist"
                }
            }
        }},
        500: {**common_responses[500]}
    }
)    
async def get_film_details(
    film_id: UUID,
    session: AsyncSession = Depends(db_session),
):
    try:
        film = await get_film_by_id(film_id, session)
    except ValueError as e:
        # Handle the case where the film does not exist
        raise HTTPException(status_code=404, detail=str(e))
    
    return film

