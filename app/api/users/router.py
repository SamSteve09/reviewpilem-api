from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.api.response_code import common_responses
from app.deps.pagination import pagination_params
from app.api.users.schemas import(
    UserUpdate, UserRegister, UserResponse, UserUpdatePassword, 
)
from app.api.users.schemas import UserProfile
from app.api.users.service import(
    create_user, get_user_by_id, get_user_profile,
    update_user_by_id, change_user_password,
)
from app.api.auth.hash import hash_password
from app.api.auth.deps import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=201,
             responses={
        400: {**common_responses[400], "content": {
            "application/json": {
                "example": {
                    "detail": "Username with name {username} already used"
                }
            }
        }},
        500: common_responses[500]
    })
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
    

@router.get("/me", response_model=UserProfile, responses={401: {**common_responses[401],},500: common_responses[500]})
async def get_me(session: AsyncSession = Depends(db_session),pagination: dict = Depends(pagination_params), current_user=Depends(get_current_user)):
    current_user = await get_user_by_id(UUID(current_user["user_id"]), session)
    profile = await get_user_profile(current_user.username, pagination, True, session)
    
    return profile

@router.patch("/me", response_model=UserResponse, responses={401: {**common_responses[401], 500: common_responses[500]}})
async def update_my_data(request: UserUpdate, session: AsyncSession = Depends(db_session), sub = Depends(get_current_user)):

    user = await update_user_by_id(sub["user_id"], request, session)
    
    return user

@router.patch("/me/password")
async def update_my_password(request: UserUpdatePassword, session: AsyncSession = Depends(db_session), sub = Depends(get_current_user)):
    
    try:
        user = await change_user_password(sub["user_id"], request.password, request.new_password, session)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    return {"message": "Password updated successfully"}

@router.get("/{username}", response_model=UserProfile, responses = {
    404: {**common_responses[404], "content": {
        "application/json": {
            "example": {
                "detail": "User does not exist"
            }
        }
    }},
    500: common_responses[500]
})
async def get_user(username: str, pagination: dict = Depends(pagination_params),session: AsyncSession = Depends(db_session)):
    try:
        user = await get_user_profile(username, pagination, False, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return user
