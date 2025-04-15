from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID

class GenreFilm(SQLModel,table = True):
    film_id: UUID = Field(default_factory=uuid4, primary_key=True, foreign_key="film.id")
    genre_id: int = Field(default_factory=uuid4, primary_key=True, foreign_key="genre.id")
