from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.db.db import db_session
from app.db.models import User
from app.api.users.service import update_password

from .hash import verify_hash,check_needs_rehash
from .token import create_access_token, create_refresh_token, decode_token
from .schemas import Token

from app.api.response_code import common_responses

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token, responses={ 401: {**common_responses[401], "content": {
    "application/json": {
        "example": {
            "detail": "Incorrect credentials"
        }
    }
    }},500: {**common_responses[500]}})
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_session)) -> Token:
    result = await session.exec(select(User).where(User.username == data.username))
    user = result.one_or_none()
    if not user or not verify_hash(user.password_hash, data.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials",headers={"WWW-Authenticate": "Bearer"},)

    #token_data = {"sub": user.id, "role": user.role}
    if check_needs_rehash(user.password_hash):
        user = await update_password(user.id, data.password)
    
    return Token(
        access_token=create_access_token(user.id, user.role)
    )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_data = {"sub": payload["sub"], "role": payload["role"]}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data)
    }
