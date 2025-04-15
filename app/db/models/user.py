from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from sqlalchemy import Text
from datetime import date
from enum import Enum
from film import FilmModel
from user_film import UserFilmModel

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserModel(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=1,max_length=255,unique=True)
    password_hash: str = Field()
    bio: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    is_private: bool = Field(default=False)
    created_at: date = Field(default=date.today())
    role: Role = Field(default=Role.USER)
    
    films: list[FilmModel] = Relationship(back_populates="users", link_model=UserFilmModel)
    
    