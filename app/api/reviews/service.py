from uuid import UUID

from fastapi import Depends
from sqlmodel import select, join
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.db.models import Review, UserFilm, Film, Reaction
from app.enums import UserFilmStatus, ReactionType

from .schemas import ReviewCreate, ReviewCreateResponse

async def create_review(
    user_id: UUID,
    film_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
) -> ReviewCreateResponse:
    statement = (
        select(UserFilm, Film)
        .join(Film, Film.id == UserFilm.film_id)
        .where(
            UserFilm.user_id == user_id,
            UserFilm.film_id == film_id
        )
    )
    result = await session.exec(statement)
    temp = result.first()
    user_film = temp[0] if temp else None
    film = temp[1] if temp else None
    
    if user_film is None:
        raise ValueError("You haven't added this film yet")
    elif user_film.status == UserFilmStatus.PLAN_TO_WATCH:
        raise ValueError("You cannot add a review to a film that you haven't watched yet")

    review = Review(
        user_film_id=user_film.id,
        rating=request.rating,
        comment=request.comment,
    )
    session.add(review)

    #await session.refresh(review)
    
    new_rating = ((film.rating * film.rating_count) + request.rating) / (film.rating_count + 1)
    film.rating = new_rating
    film.rating_count += 1
    session.add(film)
    await session.commit()
    review = ReviewCreateResponse(
        id=review.id,
        film_id=film_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )
    return review

async def get_review_by_review_id(
    id: UUID, session: AsyncSession = Depends(db_session)
) -> Review | None:
    statement = select(Review).where(Review.id == id)
    result = await session.exec(statement)
    return result.first()

async def react_to_review(
    user_id: UUID,
    review_id: UUID,
    reaction: ReactionType,
    session: AsyncSession = Depends(db_session),
) -> Review :
    #reaction = ReactionType(reaction)
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    statement2 = select(Reaction).where(Reaction.user_id == user_id, Reaction.review_id == review_id)
    result2 = await session.exec(statement2)
    existing_reaction = result2.first()
    if existing_reaction: 
        if existing_reaction.reaction_type == reaction:
            raise ValueError("You have already reacted to this review, use delete method to remove your reaction")
        # if the reaction is different, update the like/dislike count
        if existing_reaction.reaction_type == ReactionType.LIKE:
            review.like_count -= 1
            
        elif existing_reaction.reaction_type == ReactionType.DISLIKE:
            review.dislike_count -= 1
        existing_reaction.reaction_type = reaction
    if reaction == ReactionType.LIKE:
        review.like_count += 1
    elif reaction == ReactionType.DISLIKE:
        review.dislike_count += 1
    react = Reaction(
        user_id=user_id,
        review_id=review_id,
        reaction_type=reaction,
    )
    session.add(review)
    session.add(react)
    await session.commit()
    
    return react
async def unreact_to_review(
    user_id: UUID,
    review_id: UUID,
    reaction: ReactionType,
    session: AsyncSession = Depends(db_session),
) -> Review :
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    statement2 = select(Reaction).where(Reaction.user_id == user_id, Reaction.review_id == review_id)
    result2 = await session.exec(statement2)
    existing_reaction = result2.first()
    
    if existing_reaction is None:
        raise ValueError("You have not reacted to this review yet")
    
    if existing_reaction.reaction_type == ReactionType.LIKE:
        review.like_count -= 1
    elif existing_reaction.reaction_type == ReactionType.DISLIKE:
        review.dislike_count -= 1
    
    await session.delete(existing_reaction)
    session.add(review)
    await session.commit()
    
    return review
async def delete_review(
    review_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> Review | None:
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    statement2 = select(Reaction).where(Reaction.user_id == user_id, Reaction.review_id == review_id)
    result2 = await session.exec(statement2)
    existing_reaction = result2.first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == ReactionType.LIKE:
            review.like_count -= 1
        elif existing_reaction.reaction_type == ReactionType.DISLIKE:
            review.dislike_count -= 1
        await session.delete(existing_reaction)
    
    await session.delete(existing_reaction)
    await session.add(review)
    await session.commit()
    
    return review
async def delete_reaction(
    review_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> Review | None:
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    
    statement2 = select(Reaction).where(Reaction.user_id == user_id, Reaction.review_id == review_id)
    result2 = await session.exec(statement2)
    existing_reaction = result2.first()
    
    if existing_reaction is None:
        raise ValueError("You have not reacted to this review yet")
    
    await session.delete(review)
    await session.commit()
    
    return {}
async def update_review(
    review_id: UUID,
    user_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
) -> Review | None:
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    if review.user_film.user_id != user_id:
        raise ValueError("You are not authorized to update this review")
    
    review.rating = request.rating
    review.comment = request.comment
    
    session.add(review)
    await session.commit()
    
    return review