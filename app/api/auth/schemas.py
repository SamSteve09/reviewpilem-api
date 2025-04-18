from pydantic import BaseModel
from uuid import UUID


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: UUID
    role: str

class UserLogin(BaseModel):
    username: str
    password: str