from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID
from enum import Enum

class UserFilmStatus(str, Enum):
    PLAN_TO_WATCH = "plan_to_watch"
    WATCHING = "watching"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"

class UserFilmModel(SQLModel,table = True):
    id: int = Field(default_factory=uuid4, primary_key=True)
    status: UserFilmStatus = Field()
    user_id: UUID = Field(foreign_key="usermodel.id")
    film_id: UUID = Field(foreign_key="filmmodel.id")
    progress: int = Field(default=0)