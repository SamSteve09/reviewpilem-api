from sqlmodel import Field, SQLModel,Relationship
from film import FilmModel
from genre_film import GenreFilmModel
from typing import List

class GenreModel(SQLModel,table = True):
    id: int = Field(defaul=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)
    
    films: List[FilmModel] = Relationship(back_populates="genres", link_model=GenreFilmModel)
