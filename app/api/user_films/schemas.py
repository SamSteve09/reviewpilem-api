from uuid import UUID
from pydantic import BaseModel

class UserAddFilm(BaseModel):
    status: str | None = None
    progress: int | None = None
    
class UserFilmResponse(BaseModel):
    film_id: UUID
    status: str | None = None
    progress: int | None = None
    
class UserFilmListResponse(BaseModel):
    username: str
    films: list[UserFilmResponse] | None = None

    class Config:
        orm_mode = True
        
class UserFilmOut(BaseModel):
    film_title: str
    status: str
    progress: int