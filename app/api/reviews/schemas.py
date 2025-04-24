from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    rating: int | None = None
    comment: str | None = None
    
class ReviewCreateResponse(BaseModel):
    id: UUID
    film_id: UUID
    rating: int | None = None
    comment: str | None = None
    created_at: datetime | None = None

class ReviewUpdate(BaseModel):
    id: UUID
    film_id: UUID
    rating: int | None = None
    comment: str | None = None
    last_updated_at: datetime | None = None
    
class ReviewResponse(BaseModel):
    film: str
    author : str
    rating: int | None = None
    comment: str | None = None
    like_count: int | None = None
    dislike_count: int | None = None
    created_at: datetime | None = None
    last_updated_at: datetime | None = None
    