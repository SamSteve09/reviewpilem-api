from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import UniqueConstraintViolation
from app.db.db import db_session
from app.api.response_code import common_responses
from app.deps.pagination import pagination_params
from app.api.user_films.schemas import UserFilmResponse
from app.db.models import Reaction, ReactionType, Review
from .service import (
    create_review, get_review_by_review_id,
    react_to_review,unreact_to_review, delete_review_by_review_id,
    update_review_by_review_id, get_review_by_film_id,
    get_review_by_username
)
from .schemas import ReviewCreate, ReviewCreateResponse, ReviewUpdate, ReviewResponse

from app.api.users.service import get_user_by_id
from app.api.auth.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post(
    "/{film_id}",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {**common_responses[400], "content": {
                "application/json": {
                    "examples": {
                        "Not in user film list":{
                            "value" : {"detail":"You haven't added this film yet"}
                        },
                        "Have not watched movie": {
                            "value" : {"detail":"You cannot add a review to a film that you haven't watched yet}"}
                        }
                    }
                }}},401: {**common_responses[401]},404: {**common_responses[404],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "Film with id {film_id} does not exist"
                    }
                }
            }},500: {**common_responses[500]}})
async def write_review(
    film_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
) -> UserFilmResponse:
    user_id = sub["user_id"]
    try:
        film = await create_review(user_id, film_id, request, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film with id {film_id} does not exist")
    
    return film

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    responses={401: {**common_responses[401]}, 
               403: {**common_responses[403],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "You are not authorized to delete this review"
                    }
                }}}, 
               404: {**common_responses[404],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "Review with id {review_id} does not exist"
                    }
                }
            }},500: {**common_responses[500]}}
)
async def delete_review(
    review_id: UUID,
    session: AsyncSession = Depends(db_session),
    sub = Depends(get_current_user),
):
    user_id = sub["user_id"]
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        deleted_review = await delete_review_by_review_id(user_id, review_id, session)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this review")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return deleted_review

@router.get(
    "/film/{film_id}",
    response_model=list[ReviewResponse] | None,
    status_code=status.HTTP_200_OK,
    responses={404: {**common_responses[404],
    "content": {
    "application/json": {
        "example": {
            "detail": "Film with id {film_id} does not exist"
        }
    }}}, 500: {**common_responses[500]}}
)
async def get_movie_reviews(
    film_id: UUID,
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session),
):
    try:
        reviews = await get_review_by_film_id(film_id, pagination, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return reviews


@router.get(
    "/user/{username}",
    response_model=list[ReviewResponse] | None,
    status_code=status.HTTP_200_OK,
    responses={404: {**common_responses[404],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "User with username {username} does not exist"
                    }
                }}}, 500: {**common_responses[500]}}
)
async def get_user_reviews(
    username: str,
    pagination: dict = Depends(pagination_params),
    session: AsyncSession = Depends(db_session),
):
    try:
        reviews = await get_review_by_username(username, pagination, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return reviews


@router.patch(
    "/{review_id}",
    response_model=ReviewUpdate,
    status_code=status.HTTP_200_OK,
    responses={401: {**common_responses[401]}, 
            403: {**common_responses[403],
            "content": {
            "application/json": {
                "example": {
                    "detail": "You are not authorized to update this review"
                }
            }}}, 
            404: {**common_responses[404],
            "content": {
            "application/json": {
                "example": {
                    "detail": "Review with id {review_id} does not exist"
                }
            }
        }},500: {**common_responses[500]}}
)

async def update_review(
    review_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
    sub = Depends(get_current_user),
):
    user_id = sub["user_id"]
    try:
        updated_review = await update_review_by_review_id(user_id, review_id, request, session)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this review")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated_review

@router.get(
    "/{review_id}",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {**common_responses[404],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "Review with id {review_id} does not exist"
                    }
                }
            }},500: {**common_responses[500]}}
)
async def get_review(
    film_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> ReviewCreate:
    review = await get_review_by_review_id(film_id, session)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review

@router.put(
    "/{review_id}/react",
    response_model=Reaction,
    status_code=status.HTTP_200_OK,
    responses={
            401: {**common_responses[401]},
               404: {**common_responses[404],
                "content": {
                "application/json": {
                    "example": {
                        "detail": "Review with id {review_id} does not exist"
                    }
                }}},
                409: {**common_responses[409],
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "You have already reacted the same reaction to this review, use delete method to remove your reaction"
                            }
                        }
                    }    
            },500: {**common_responses[500]}}
)
async def react_a_review(
    review_id: UUID,
    reaction_type: ReactionType,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
) -> Reaction:
    print(reaction_type)
    user_id = sub["user_id"]
    try:
        new_reaction = await react_to_review(user_id, review_id, reaction_type, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UniqueConstraintViolation as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return new_reaction

@router.delete(
    "/{review_id}/react",
    status_code=status.HTTP_200_OK,
    responses={401: {**common_responses[401]},
            404: {**common_responses[404],
            "content": {
            "application/json": {
                "example": {
                    "detail": "Review with id {review_id} does not exist"
                }
            }}},500: {**common_responses[500]}}
)
async def delete_reaction(
    review_id: UUID,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
):
    user_id = sub["user_id"]

    try:
        deleted_reaction = await unreact_to_review(user_id, review_id, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Reaction successfully deleted", "review_id": review_id}