from pydantic import BaseModel
from uuid import UUID
from datetime import date

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
    id: UUID
    title: str
    release_date: date | None = None
    air_status: str
    film_type: str
    episode_count: int | None = None
    rating: float | None = None
    cover_image: str | None = None
    
class FilmDetail(BaseModel):
    title: str
    synopsis: str | None = None
    release_date: date | None = None
    air_status: str
    film_type: str
    episode_count: int | None = None
    rating: float | None = None
    rating_count: int | None = None
    genres: list[str] | None = None
    images: list[str] | None = None
    