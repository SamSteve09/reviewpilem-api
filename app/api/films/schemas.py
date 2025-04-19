from pydantic import BaseModel
from fastapi import UploadFile
from uuid import UUID
from datetime import date, datetime

class FilmCreate(BaseModel):
    title: str
    synopsis: str | None = None
    release_date: date | None = None
    air_status: str
    film_type: str
    episode_count: int | None = None
    rating: float | None = None
    genres: list[str] | None = None
    
class FilmSummary(BaseModel):
    title: str
    release_date: date | None = None
    air_status: str
    film_type: str
    episode_count: int | None = None
    rating: float | None = None
    
class FilmDetail(FilmSummary):
    title: str
    synopsis: str | None = None
    release_date: date | None = None
    air_status: str
    film_type: str
    episode_count: int | None = None
    rating: float | None = None
    rating_count: int | None = None
    user_rating: float | None = None
    genres: list[str] | None = None
    images: list[str] | None = None
    