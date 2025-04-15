from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from sqlalchemy import Text
from datetime import date
from enum import Enum
from genre import Genre
from user import User
from genre_film import GenreFilm
from user_film import UserFilm

class FilmStatus(str, Enum):
    NOT_YET_AIRED = "not_yet_aired"
    AIRING = "airing"
    FINISHED_AIRING = "finished_airing"

class Film(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1,max_length=255)
    synopsis: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    release_date: date = Field(nullable=True)
    air_status: FilmStatus = Field()
    episode_count: int = Field(default=1)
    rating: float = Field(default=0,nullable=True)
    
    genres: list[Genre] = Relationship(back_populates="films", link_model=GenreFilm)
    users: list[User] = Relationship(back_populates="films", link_model=UserFilm)