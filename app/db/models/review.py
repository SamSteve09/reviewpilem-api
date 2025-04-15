from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from sqlalchemy import Text
from user_film import UserFilm
from reaction import Reaction
#from datetime import datetime

class Review(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_film_id: int = Field(foreign_key="userfilm.id")
    rating: int = Field(ge=1, le=10)
    comment: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    like_count: int = Field(default=0)
    dislike_count: int = Field(default=0)
    #created_at: datetime = Field(default_factory=datetime.now)
    #last_updated_at: datetime = Field(nullable=True)
    
    user_film: UserFilm = Relationship(back_populates="reviews")
    reactions: list[Reaction] = Relationship(back_populates="reviews")
    