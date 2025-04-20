from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.users.schemas import(
    UserUpdate, UserRegister, UserResponse, UserUpdatePassword, 
)
from app.api.users.service import(
    create_user, get_user_by_id, get_user_by_username,
    update_user_by_id, change_user_password,
)
from app.api.auth.hash import hash_password
from app.api.auth.deps import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    request: UserRegister,
    session: AsyncSession = Depends(db_session)
):
    hashed_password = hash_password(request.password)
    try:
        new_user = await create_user(request.username, hashed_password, request.display_name, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_user
    

@router.get("/me", response_model=UserResponse)
async def get_me(session: AsyncSession = Depends(db_session), current_user=Depends(get_current_user)):
    current_user = await get_user_by_id(UUID(current_user["user_id"]), session)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    
    return current_user

@router.patch("/me")
async def update_my_data(request: UserUpdate, session: AsyncSession = Depends(db_session), sub = Depends(get_current_user)):

    user = await update_user_by_id(sub["user_id"], request, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    
    return user

@router.patch("/me/password")
async def update_my_password(request: UserUpdatePassword, session: AsyncSession = Depends(db_session), sub = Depends(get_current_user)):
    user = await change_user_password(sub["user_id"], request.password, request.new_password, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    
    return user

@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, session: AsyncSession = Depends(db_session)):
    user = await get_user_by_username(username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    
    return user
