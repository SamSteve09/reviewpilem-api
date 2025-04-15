from sqlmodel import Field, SQLModel,Relationship
from film import Film
from genre_film import GenreFilm

class Genre(SQLModel,table = True):
    id: int = Field(defaul=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)
    
    films: list[Film] = Relationship(back_populates="genres", link_model=GenreFilm)
