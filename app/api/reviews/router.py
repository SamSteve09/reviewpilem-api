from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.user_films.schemas import(
    UserAddFilm, UserFilmResponse
)
from app.db.models import Reaction, ReactionType
from .service import create_review, get_review_by_review_id, react_to_review,unreact_to_review
from .schemas import ReviewCreate, ReviewCreateResponse

from app.api.users.service import get_user_by_id
from app.api.auth.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post(
    "/{film_id}",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def write_review(
    film_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
) -> UserFilmResponse:
    user_id = sub["user_id"]
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        film = await create_review(user_id, film_id, request, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
    
    return film

@router.get(
    "/{review_id}",
    response_model=ReviewCreateResponse,
    status_code=status.HTTP_200_OK,
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
)
async def react_a_review(
    review_id: UUID,
    reaction_type: ReactionType,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
) -> Reaction:
    print(reaction_type)
    user_id = sub["user_id"]
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        new_reaction = await react_to_review(user_id, review_id, reaction_type, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_reaction

@router.delete(
    "/{review_id}/react",
    status_code=status.HTTP_200_OK,
)
async def delete_reaction(
    review_id: UUID,
    session: AsyncSession = Depends(db_session),
    sub  = Depends(get_current_user),
):
    user_id = sub["user_id"]

    try:
        deleted_reaction = await unreact_to_review(user_id, review_id, None, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return deleted_reaction