from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from review import Review
from uuid import uuid4, UUID

class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    
class Reaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    review_id: UUID = Field(foreign_key="review.id")
    reaction_type: ReactionType = Field()

    review: Review = Relationship(back_populates="reactions")