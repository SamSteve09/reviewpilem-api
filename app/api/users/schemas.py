from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.api.user_films.schemas import UserFilmOut

class UserRegister(BaseModel):
    username: str
    password: str 
    display_name: str

class UserResponse(BaseModel):
    username: str
    display_name: str
    bio: str | None
    is_private: bool | None
    created_at: datetime
    last_updated_at: datetime
    
class UserUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    is_private: bool | None = None
    
class UserUpdatePassword(BaseModel):
    password: str
    new_password: str

    
class UserProfile(BaseModel):
    username: str
    display_name: str
    bio: str | None = None
    is_private: bool | None
    created_at: datetime
    films: list[UserFilmOut] | None = None

