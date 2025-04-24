from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.deps.pagination import pagination_params
from app.api.user_films.schemas import(
    UserAddFilm, UserFilmResponse, UserFilmOut
)
from .service import create_user_film, update_user_film_by_id, get_a_user_user_film_list

from app.api.users.service import get_user_by_id
from app.api.auth.deps import get_current_user

router = APIRouter(prefix="/user-films", tags=["User Films"])

@router.get("/{user_id}", response_model=list[UserFilmOut])
async def get_user_film_list(
    user_id: UUID,
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session),
):  
    try:
        user_film_list = await get_a_user_user_film_list(user_id, pagination, session)
        if user_film_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User have private film list",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return user_film_list

@router.post("/{film_id}", status_code=201,response_model=UserFilmResponse)
async def add_user_film(
    film_id: UUID,
    request: UserAddFilm, session: AsyncSession = Depends(db_session), 
    user_id = Depends(get_current_user)
):
    user = await get_user_by_id(user_id["user_id"], session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
        
    try:
        new_user_film = await create_user_film(
            user_id["user_id"], film_id, request.status, request.progress, session
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return new_user_film

@router.patch("/{film_id}", response_model=UserFilmResponse)
async def update_user_film(
    film_id: UUID,
    request: UserAddFilm, session: AsyncSession = Depends(db_session), 
    user_id = Depends(get_current_user)
):
    user = await get_user_by_id(user_id["user_id"], session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
        
    try:
        updated_user_film = await update_user_film_by_id(
            user_id["user_id"], film_id, request.status, request.progress, session
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return updated_user_film



