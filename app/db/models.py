from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from datetime import date,datetime
from typing import Text
from app.enums import FilmStatus, Role, UserFilmStatus, ReactionType, FilmType

class GenreFilm(SQLModel,table = True):
    film_id: UUID = Field(primary_key=True, foreign_key="film.id", ondelete="CASCADE")
    genre_id: int | None = Field(default=None,primary_key=True, foreign_key="genre.id",ondelete="CASCADE")
    
class UserFilm(SQLModel,table = True):
    id: int | None = Field(default=None,primary_key=True)
    status: UserFilmStatus
    user_id: UUID = Field(default_factory=uuid4, foreign_key="user.id", ondelete="CASCADE")
    film_id: UUID = Field(default_factory=uuid4, foreign_key="film.id", ondelete="CASCADE")
    progress: int = Field(default=0)
    
class Genre(SQLModel,table = True):
    id: int = Field(default=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)
    
    films: list["Film"] = Relationship(back_populates="genres", link_model=GenreFilm,cascade_delete=True)
    
class User(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=1,max_length=255,unique=True,index=True)
    password_hash: str
    bio: str | None = Field(default=None,nullable=True,sa_column_kwargs={"type_": Text})
    is_private: bool = Field(default=False)
    created_at: date = Field(default=date.today())
    role: Role = Field(default=Role.USER)
    
    films: list["Film"] = Relationship(back_populates="users", link_model=UserFilm,cascade_delete=True)
    
class Film(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1,max_length=255)
    synopsis: str | None = Field(sa_column_kwargs={"type_": Text})
    release_date: date | None = Field(default=None, nullable=True)
    air_status: FilmStatus
    film_type: FilmType
    episode_count: int | None = Field(default=None, nullable=True)
    rating: float | None = Field(default=None, ge=0, le=10, nullable=True)
    rating_count: int | None = Field(default=0, nullable=True)
    
    genres: list["Genre"] = Relationship(back_populates="films", link_model=GenreFilm,cascade_delete=True)
    users: list["User"] = Relationship(back_populates="films", link_model=UserFilm,cascade_delete=True)

class Reaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id") # reaction from a deleted user won't go away
    review_id: UUID = Field(foreign_key="review.id", ondelete="CASCADE")
    reaction_type: ReactionType = Field()

    review: "Review" = Relationship(back_populates="reaction")
    
class Review(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # delete review if film is deleted from user list (implicitly delete if either film or user is also deleted)
    user_film_id: int = Field(foreign_key="userfilm.id",ondelete="CASCADE")
    rating: int = Field(ge=1, le=10)
    comment: str | None = Field(sa_column_kwargs={"type_": Text})
    like_count: int = Field(default=0)
    dislike_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    #user_films: "UserFilm" = Relationship(back_populates="reviews")
    reactions: list["Reaction"] = Relationship(back_populates="review",cascade_delete=True)
    

    

    


