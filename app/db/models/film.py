from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID
from sqlalchemy import Text
from datetime import date
from enum import Enum

class FilmStatus(str, Enum):
    NOT_YET_AIRED = "not_yet_aired"
    AIRING = "airing"
    FINISHED_AIRING = "finished_airing"

class FilmModel(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1,max_length=255)
    synopsis: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    release_date: date = Field(nullable=True)
    air_status: FilmStatus = Field()
    episode_count: int = Field(default=1)
    rating: float = Field(default=0,nullable=True)