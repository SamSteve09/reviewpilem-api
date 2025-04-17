from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from datetime import date,datetime
from typing import Text
from enums import FilmStatus, Role, UserFilmStatus, ReactionType

class GenreFilm(SQLModel,table = True):
    film_id: UUID = Field(default_factory=uuid4, primary_key=True, foreign_key="film.id")
    genre_id: int | None = Field(default_factory=uuid4, primary_key=True, foreign_key="genre.id")
    
class UserFilm(SQLModel,table = True):
    id: int | None = Field(default=None,primary_key=True)
    status: UserFilmStatus
    user_id: UUID = Field(foreign_key="user.id")
    film_id: UUID = Field(foreign_key="film.id")
    progress: int = Field(default=0)
    
class Genre(SQLModel,table = True):
    id: int = Field(default=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)
    films: list["Film"] = Relationship(back_populates="genres", link_model=GenreFilm)
    
class User(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=1,max_length=255,unique=True,index=True)
    password_hash: str
    bio: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    is_private: bool = Field(default=False)
    created_at: date = Field(default=date.today())
    role: Role = Field(default=Role.USER)
    
    films: list["Film"] = Relationship(back_populates="users", link_model=UserFilm)
    
class Film(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1,max_length=255)
    synopsis: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    release_date: date = Field(nullable=True)
    air_status: FilmStatus
    episode_count: int = Field(default=1,nullable=True)
    rating: float = Field(default=0,nullable=True)
    rating_count: int = Field(default=0,nullable=True)
    
    genres: list["Genre"] = Relationship(back_populates="films", link_model=GenreFilm)
    users: list["User"] = Relationship(back_populates="films", link_model=UserFilm)

class Reaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    review_id: UUID = Field(foreign_key="review.id")
    reaction_type: ReactionType = Field()

    review: "Review" = Relationship(back_populates="reactions")
    
class Review(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_film_id: int = Field(foreign_key="userfilm.id")
    rating: int = Field(ge=1, le=10)
    comment: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    like_count: int = Field(default=0)
    dislike_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(nullable=True)
    
    user_film: UserFilm = Relationship(back_populates="reviews")
    reactions: list["Reaction"] = Relationship(back_populates="reviews")
    

    

    


