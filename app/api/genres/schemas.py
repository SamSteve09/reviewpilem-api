from pydantic import BaseModel

class CreateGenre(BaseModel):
    genre_name: str
