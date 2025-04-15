from sqlmodel import Field, SQLModel

class GenreModel(SQLModel,table = True):
    id: int = Field(defaul=None, primary_key=True)
    genre_name: str = Field(min_length=1,max_length=255,unique=True)

