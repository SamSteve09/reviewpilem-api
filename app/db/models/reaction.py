from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from review import ReviewModel
from uuid import uuid4, UUID

class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    
class ReactionModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="usermodel.id")
    review_id: UUID = Field(foreign_key="reviewmodel.id")
    reaction_type: ReactionType = Field()

    review: ReviewModel = Relationship(back_populates="reactions")