from uuid import UUID

from fastapi import Depends
from sqlmodel import select, join
from sqlalchemy.sql import expression
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.exceptions import UniqueConstraintViolation
from app.db.models import Review, UserFilm, Film, Reaction, User
from app.enums import UserFilmStatus, ReactionType

from .schemas import ReviewCreate, ReviewCreateResponse, ReviewUpdate, ReviewResponse

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
        user_id=user_id,
        film_id=film_id,
        rating=request.rating,
        comment=request.comment,
    )
    session.add(review)
    
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

async def get_review_by_film_id(
    film_id: UUID, pagination: dict, session: AsyncSession = Depends(db_session)
) -> list[Review] | None:
    statement1 = select(Film).where(Film.id == film_id)
    result1 = await session.exec(statement1)
    film = result1.first()
    
    if film is None:
        raise ValueError("Film not found")
    
    statement = select(Review,User.username).where(Review.film_id == film_id).join(
        User, Review.user_id == User.id).offset(pagination["offset"]).limit(pagination["limit"])
    result = await session.exec(statement)
    reviews = result.all()

    if not reviews:
        raise ValueError("No reviews found for this film")

    review_responses = []
    for review in reviews:
        
        review_response = ReviewResponse(
            film= film.title,
            author=review[1],
            rating=review[0].rating,
            comment=review[0].comment,
            like_count=review[0].like_count,
            dislike_count=review[0].dislike_count,
            created_at=review[0].created_at,
            last_updated_at=review[0].last_updated_at,
        )
        review_responses.append(review_response)


    return review_responses

async def get_review_by_username(
    username: str, pagination: dict, session: AsyncSession = Depends(db_session)
) -> list[ReviewResponse] | None:
    statement = select(User.id).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise ValueError("User not found")

    statement2 = select(Review,Film.title).where(Review.user_id == user).join(Film, Film.id == 
                Review.film_id).offset(pagination["offset"]).limit(pagination["limit"])
    result2 = await session.exec(statement2)
    reviews = result2.all()

    if not reviews:
        raise ValueError("No reviews found for this user")
    
    review_responses = []
    for review in reviews:
        
        review_response = ReviewResponse(
            film= review[1],
            author=username,
            rating=review[0].rating,
            comment=review[0].comment,
            like_count=review[0].like_count,
            dislike_count=review[0].dislike_count,
            created_at=review[0].created_at,
            last_updated_at=review[0].last_updated_at,
        )
        review_responses.append(review_response)


    return review_responses

async def react_to_review(
    user_id: UUID,
    review_id: UUID,
    reaction: ReactionType,
    session: AsyncSession = Depends(db_session),
) -> Reaction:
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
            raise UniqueConstraintViolation("You have already reacted the same reaction to this review, use delete method to remove your reaction")
        # if the reaction is different, update the like/dislike count
        if existing_reaction.reaction_type == ReactionType.LIKE:
            review.like_count -= 1
            review.dislike_count += 1
        elif existing_reaction.reaction_type == ReactionType.DISLIKE:
            review.dislike_count -= 1
            review.like_count += 1
        existing_reaction.reaction_type = reaction
        session.add(existing_reaction)
        session.add(review)
        await session.commit()
        await session.refresh(existing_reaction)
        await session.refresh(review)
        return existing_reaction
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
    await session.refresh(review)
    await session.refresh(react)
    
    return react
async def unreact_to_review(
    user_id: UUID,
    review_id: UUID,
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
    await session.refresh(review)
    
    return review

async def delete_review_by_review_id(
    user_id: UUID,
    review_id: UUID,
    session: AsyncSession = Depends(db_session),
):
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")

    # bruh
    if str(review.user_id) != str(user_id):
        raise PermissionError("You are not authorized to delete this review")
    
    statement2 = select(Film).where(Film.id == review.film_id)
    result2 = await session.exec(statement2)
    film = result2.first()
    
    film.rating = ((film.rating * film.rating_count) - review.rating) / (film.rating_count - 1) if film.rating_count > 1 else 0
    film.rating_count -= 1
    session.add(film)
    await session.delete(review)
    await session.commit()
    await session.refresh(film)
    
    return {"message": "Review successfully deleted", "review_id": review_id}

async def update_review_by_review_id(
    user_id: UUID,
    review_id: UUID,
    request: ReviewCreate,
    session: AsyncSession = Depends(db_session),
) -> Review | None:
    statement = select(Review).where(Review.id == review_id)
    result = await session.exec(statement)
    review = result.first()
    
    if review is None:
        raise ValueError("Review not found")
    
    if str(review.user_id) != str(user_id):
        raise PermissionError("You are not authorized to update this review")
    
    statement2 = select(Film).where(Film.id == review.film_id)
    result2 = await session.exec(statement2)
    film = result2.first()
    film.rating = ((film.rating * film.rating_count) - review.rating + request.rating) / film.rating_count
    
    review.rating = request.rating
    review.comment = request.comment
    
    session.add(review)
    session.add(film)
    
    await session.commit()
    
    review = ReviewUpdate(
        id=review.id,
        film_id=review.film_id,
        rating=review.rating,
        comment=review.comment,
        last_updated_at=review.last_updated_at,
    )
    
    return review