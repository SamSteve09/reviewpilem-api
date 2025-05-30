from uuid import UUID

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.db.models import User,Film, UserFilm
from app.enums import FilmStatus, UserFilmStatus
from .schemas import UserFilmOut


async def create_user_film(id: UUID, film_id: UUID, status: str, progress: int, session: AsyncSession = Depends(db_session)):
    statement = select(User).where(User.id == id)
    result = await session.exec(statement)
    user = result.first()

    if user is None: #should not happen because authentication is done before this function
        raise ValueError(f"User with id {id} does not exist")
    
    statement2 = select(Film).where(Film.id == film_id)
    result2 = await session.exec(statement2)
    film = result2.first()
    
    if film is None:
        raise ValueError(f"Film with id {film_id} does not exist")
    status = UserFilmStatus(status)

    if film.air_status == FilmStatus.NOT_YET_AIRED and (status != "plan_to_watch" or progress > 0):
        raise ValueError(f"Film with id {film_id} is not yet aired")
    elif progress > film.episode_count:
        raise ValueError(f"Progress cannot be greater than {film.episode_count}")
    
    statement3 = select(UserFilm).where(UserFilm.film_id == film_id and UserFilm.user_id == id)
    result3 = await session.exec(statement3)
    existing_user_film = result3.first()
    if existing_user_film:
        raise ValueError(f"UserFilm with film id {film_id} for this user already exists")

    user_film = UserFilm(
        user_id=id,
        film_id=film_id,
        status=UserFilmStatus(status),
        progress=progress,
    )
    session.add(user_film)
    await session.commit()
    await session.refresh(user_film)

    return user_film

async def update_user_film_by_id(
    id: UUID, film_id : UUID, status: str, progress: int, session: AsyncSession = Depends(db_session)
):

    statement = select(UserFilm).where(UserFilm.film_id == film_id and UserFilm.user_id == id)
    result = await session.exec(statement)
    user_film = result.first()

    if user_film is None:
        raise ValueError(f"UserFilm with film id {film_id} for this user does not exist")
    
    statement2 = select(Film).where(Film.id == film_id)
    result2 = await session.exec(statement2)
    film = result2.first()
    user_film.status = UserFilmStatus(status) 
    
    if film.air_status == FilmStatus.NOT_YET_AIRED and (status != "plan_to_watch" or progress > 0):
        raise ValueError(f"Film with id {film_id} is not yet aired")
    elif progress > film.episode_count:
        raise ValueError(f"Progress cannot be greater than {film.episode_count}")

    user_film.progress = progress

    session.add(user_film)
    await session.commit()
    await session.refresh(user_film)

    return user_film

async def get_a_user_user_film_list(
    id: UUID, pagination: dict, from_self: bool, session: AsyncSession = Depends(db_session)
) -> list[UserFilmOut] | None:
    statement = select(User).where(User.id == id).offset(pagination["offset"]).limit(pagination["limit"])
    result = await session.exec(statement)
    user = result.first()
    
    if user is None:
        raise ValueError(f"User with id {id} does not exist")
    elif user.is_private == True and from_self == False:
        raise PermissionError(f"User with id {id} has private film list")
    
    statement2 = select(UserFilm,Film).join(Film).where(UserFilm.user_id == user.id and UserFilm.film_id == Film.id)
    result2 = await session.exec(statement2)
    user_film = result2.all()
    user_films : list[UserFilmOut] = []
    for row in user_film:
        user_films.append(UserFilmOut(film_id=row[1].id,film_title=row[1].title,status=row[0].status,progress=row[0].progress))
    return user_films