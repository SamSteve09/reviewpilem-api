from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from pydantic import TypeAdapter
from app.db.db import db_session
from app.db.models import Film
from sqlmodel import select
from app.enums import Role
from app.api.auth.deps import require_role

from .service import create_film
from .schemas import FilmCreate

router = APIRouter(prefix="/films", tags=["Films"])

@router.post(
    "/",
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
    
async def get_film_detail(
    film_id: str,
    session: AsyncSession = Depends(db_session),
):
    statement = select(Film).where(Film.id == film_id)
    result = await session.exec(statement)
    film = result.first()
    
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    
    return film