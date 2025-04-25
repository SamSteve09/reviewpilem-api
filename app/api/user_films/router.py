from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.response_code import common_responses
from app.deps.pagination import pagination_params
from app.api.user_films.schemas import(
    UserAddFilm, UserFilmResponse, UserFilmOut
)
from .service import create_user_film, update_user_film_by_id, get_a_user_user_film_list

from app.api.users.service import get_user_by_id
from app.api.auth.deps import get_current_user

router = APIRouter(prefix="/user-films", tags=["User Films"])

@router.get("/me", response_model=list[UserFilmOut], 
            responses={401: {**common_responses[401],}, 500: common_responses[500]})
async def get_my_film_list(
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session),
    sub = Depends(get_current_user)
):  
    user_film_list = await get_a_user_user_film_list(sub["user_id"], pagination, True, session)
    
    return user_film_list

@router.get("/{user_id}", response_model=list[UserFilmOut], 
            responses={403: {**common_responses[403], "content": {
                "application/json": {
                    "example": {
                        "detail": "User with id {user_id} has private film list"
                    }
                }}
            },
            404: {**common_responses[404], "content": {
                "application/json": {
                    "example": {
                        "detail": "User with id {user_id} does not exist"
                    }
                }}
            },500: common_responses[500]})
async def get_user_film_list(
    user_id: UUID,
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session),
):  
    try:
        user_film_list = await get_a_user_user_film_list(user_id, pagination, False, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    return user_film_list

@router.post("/{film_id}", status_code=201,response_model=UserFilmResponse,
             responses={401: {**common_responses[401]}, 500: {**common_responses[500]},
            400: {**common_responses[400], "content": {
                "application/json": {
                    "examples": {
                        "User Film Already Exists": {
                            "value" : {"detail": "UserFilm with film id {film_id} for this user already exists"}
                        },
                        "Film Not Yet Aired":{
                            "value" : {"detail":"Film with id {film_id} is not yet aired"}
                        },
                        "Progress Greater Than Episode Count": {
                            "value" : {"detail":"Progress cannot be greater than {film.episode_count}"}
                        }
                    }
                }}},
            404: {**common_responses[404], "content": {
                "application/json": {
                    "example": {
                        "detail": "Film with id {film_id} does not exist"
                    }
                }}
            }})
async def add_user_film(
    film_id: UUID,
    request: UserAddFilm, session: AsyncSession = Depends(db_session), 
    user_id = Depends(get_current_user)
):
    try:
        new_user_film = await create_user_film(
            user_id["user_id"], film_id, request.status, request.progress, session
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return new_user_film

@router.patch("/{film_id}", response_model=UserFilmResponse,            
            responses={401: {**common_responses[401]}, 500: {**common_responses[500]},
            400: {**common_responses[400], "content": {
                "application/json": {
                    "examples": {
                        "Film Not Yet Aired":{
                            "value" : {"detail":"Film with id {film_id} is not yet aired"}
                        },
                        "Progress Greater Than Episode Count": {
                            "value" : {"detail":"Progress cannot be greater than {film.episode_count}"}
                        }
                    }
                }}},
            404: {**common_responses[404], "content": {
                "application/json": {
                    "examples": {
                        "User Film Not Found": {
                            "value" : {"detail": "UserFilm with film id {film_id} for this user does not exist"}
                        },
                        "Film Not Found": {
                            "value" : {"detail": "Film with id {film_id} does not exist"}
                        }
                    }
                }}
            }})
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



