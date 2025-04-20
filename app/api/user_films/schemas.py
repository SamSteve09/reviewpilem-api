from uuid import UUID
from pydantic import BaseModel

class UserAddFilm(BaseModel):
    status: str | None = None
    progress: int | None = None
    
class UserFilmResponse(BaseModel):
    film_id: UUID
    status: str | None = None
    progress: int | None = None