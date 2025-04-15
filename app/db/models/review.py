from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4, UUID
from sqlalchemy import Text
from user_film import UserFilmModel
from reaction import ReactionModel
#from datetime import datetime

class ReviewModel(SQLModel,table = True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_film_id: int = Field(foreign_key="userfilmmodel.id")
    rating: int = Field(ge=1, le=10)
    comment: str = Field(nullable=True,sa_column_kwargs={"type_": Text})
    like_count: int = Field(default=0)
    dislike_count: int = Field(default=0)
    #created_at: datetime = Field(default_factory=datetime.now)
    #last_updated_at: datetime = Field(nullable=True)
    
    user_film: UserFilmModel = Relationship(back_populates="reviews")
    reactions: list[ReactionModel] = Relationship(back_populates="reviews")
    