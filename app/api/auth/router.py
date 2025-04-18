from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.db import db_session
from app.db.models import User
from .hash import verify_hash
from .token import create_access_token, create_refresh_token, decode_token
from .schemas import UserLogin, Token
from sqlmodel import select

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(db_session)):
    result = await session.exec(select(User).where(User.username == data.username))
    user = result.one_or_none()
    if not user or not verify_hash(user.password_hash, data.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token_data = {"sub": user.id, "role": user.role}
    return {
        "access_token": create_access_token(token_data, user.role),
        "refresh_token": create_refresh_token(token_data, user.role)
    }

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
