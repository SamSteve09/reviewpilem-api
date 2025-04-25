from fastapi import Depends, UploadFile
from sqlmodel import select,func

from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.db.db import db_session
from app.db.models import Film, Genre, GenreFilm
from app.api.images.service import upload_image, get_movie_image_by_id, get_cover_image
from .schemas import FilmCreate, FilmSummary, FilmDetail
from app.enums import FilmStatus, FilmType


async def create_film(
    film: FilmCreate, images: list[UploadFile],
    session: AsyncSession = Depends(db_session), 
) -> Film:
     
    genre_ids = []
    for genre in film.genres:
        result = await session.exec(select(Genre).where(Genre.genre_name == genre))
        existing_genre = result.first()
        if not existing_genre:
            raise ValueError(f"Genre '{genre}' does not exist")
        else:
            genre_ids.append(existing_genre.id)
    #db_film = Film.model_validate(film)
    db_film = Film(
        title=film.title,
        synopsis=film.synopsis,
        release_date=film.release_date,
        air_status=FilmStatus(film.air_status),
        film_type=FilmType(film.film_type),
        episode_count=film.episode_count,
        rating=film.rating,
    )
    
    session.add(db_film)
    await session.flush() 
    session.add_all(
        GenreFilm(film_id=db_film.id, genre_id=genre_id) for genre_id in genre_ids
    )
    
    cover_image = images[0] if images else None
    if cover_image:
        new_cover = await upload_image(cover_image, db_film.id, True, session)
        session.add(new_cover)
    for image in images[1:]:
        if image:
            new_image = await upload_image(image, db_film.id, False, session)
            session.add(new_image)
    
    await session.commit()
    await session.refresh(db_film)
    return db_film

async def get_film_by_id(
    film_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> FilmDetail | None:
    exist = select(Film).where(Film.id == film_id)
    result = await session.exec(exist)
    film = result.first()
    print(film)
    
    if not film:
        raise ValueError(f"Film with id {film_id} does not exist")
    
    statement = select(Genre.genre_name).join(GenreFilm).where(GenreFilm.film_id == film.id)
    result = await session.exec(statement)
    genres = result.all()
    
    images = await get_movie_image_by_id(film_id, session)
    film = FilmDetail(
        title=film.title,
        synopsis=film.synopsis,
        release_date=film.release_date,
        air_status=film.air_status,
        film_type=film.film_type,
        episode_count=film.episode_count,
        rating=round(film.rating, 2) if film.rating is not None else None,
        rating_count=film.rating_count,
        genres=genres,
        images=images,
    )
    return film
        

async def get_all_film(
    pagination: dict,
    session: AsyncSession = Depends(db_session),
) -> list[FilmSummary]:
    statement = select(Film).offset(pagination["offset"]).limit(pagination["limit"])
    result = await session.exec(statement)
    films = result.all()
    
    film_summaries = []
    for film in films:
        film_summary = FilmSummary(
            id=film.id,
            title=film.title,
            release_date=film.release_date,
            air_status=film.air_status,
            film_type=film.film_type,
            episode_count=film.episode_count,
            rating=round(film.rating, 2) if film.rating is not None else None,
            cover_image= await get_cover_image(film.id, session),
        )
        film_summaries.append(film_summary)
            
    return film_summaries

async def search_film_by_title(
    title: str,
    pagination: dict,
    session: AsyncSession = Depends(db_session),
) -> list[FilmSummary]:
    statement = select(Film).where(func.lower(Film.title).contains(title.lower())).offset(pagination["offset"]).limit(pagination["limit"])
    result = await session.exec(statement)
    films = result.all()
    film_summaries = []
    for film in films:
        film_summary = FilmSummary(
            id=film.id,
            title=film.title,
            release_date=film.release_date,
            air_status=film.air_status,
            film_type=film.film_type,
            episode_count=film.episode_count,
            rating=round(film.rating, 2) if film.rating is not None else None,
        )
        film_summaries.append(film_summary)
            
    return film_summaries