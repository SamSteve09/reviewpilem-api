from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID

class GenreFilmModel(SQLModel,table = True):
    film_id: UUID = Field(default_factory=uuid4, primary_key=True, foreign_key="filmmodel.id")
    genre_id: int = Field(default_factory=uuid4, primary_key=True, foreign_key="genremodel.id")
