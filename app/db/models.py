from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from datetime import date,datetime
from sqlalchemy import Column,TEXT
from app.enums import FilmStatus, Role, UserFilmStatus, ReactionType, FilmType

class GenreFilm(SQLModel,table = True):
    film_id: UUID = Field(primary_key=True, foreign_key="film.id", ondelete="CASCADE")
    genre_id: int | None = Field(default=None,primary_key=True, foreign_key="genre.id",ondelete="CASCADE")
    
class UserFilm(SQLModel,table = True):
    
    user_id: UUID = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")
    film_id: UUID = Field(primary_key=True, foreign_key="film.id", ondelete="CASCADE")
    status: UserFilmStatus
    progress: int = Field(default=0, ge=0, le=2000)
    
class Genre(SQLModel,table = True):
    id: int = Field(default=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)
    
    films: list["Film"] = Relationship(back_populates="genres", link_model=GenreFilm)
    
class User(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=1,max_length=255,unique=True,index=True)
    password_hash: str
    display_name: str = Field(min_length=1,max_length=255)
    bio: str | None = Field(default=None,sa_column=Column(TEXT, nullable=True))
    is_private: bool = Field(default=False)
    role: Role = Field(default=Role.USER)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    films: list["Film"] = Relationship(back_populates="users", link_model=UserFilm)
    reactions: list["Reaction"] = Relationship(back_populates="user")
    
class Film(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1,max_length=255,index=True)
    synopsis: str | None = Field(default=None,sa_column=Column(TEXT, nullable=True))
    release_date: date | None = Field(default=None, nullable=True)
    air_status: FilmStatus
    film_type: FilmType
    episode_count: int | None = Field(default=None, nullable=True)
    rating: float | None = Field(default=None, ge=0, le=10, nullable=True)
    rating_count: int | None = Field(default=0, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    genres: list["Genre"] = Relationship(back_populates="films", link_model=GenreFilm)
    users: list["User"] = Relationship(back_populates="films", link_model=UserFilm)
    images: list["Image"] = Relationship(back_populates="film", cascade_delete=True)

class Reaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id") # reaction from a deleted user won't go away
    review_id: UUID = Field(foreign_key="review.id", ondelete="CASCADE")
    reaction_type: ReactionType = Field()

    review: "Review" = Relationship(back_populates="reactions")
    user: "User" = Relationship(back_populates="reactions")
    
class Review(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    film_id: UUID = Field(foreign_key="film.id", ondelete="CASCADE")
    rating: int = Field(ge=1, le=10)
    comment: str | None = Field(default=None,sa_column=Column(TEXT, nullable=True))
    like_count: int = Field(default=0,ge=0)
    dislike_count: int = Field(default=0,ge=0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    #user_films: "UserFilm" = Relationship(back_populates="reviews")
    reactions: list["Reaction"] = Relationship(back_populates="review",cascade_delete=True)
    
class Image(SQLModel,table = True):
    image_id: UUID = Field(default_factory=uuid4, primary_key=True)
    image_url: str = Field(min_length=1,max_length=255,unique=True,nullable=True)
    image_extension: str = Field(min_length=1,max_length=255)
    film_id: UUID = Field(foreign_key="film.id", ondelete="CASCADE")
    is_cover: bool = Field(default=False)
    
    film: Film = Relationship(back_populates="images")
    

    

    


