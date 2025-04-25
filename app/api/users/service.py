from uuid import UUID

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.db import db_session
from app.db.models import User
from .schemas import UserUpdate
from app.api.users.schemas import UserProfile
from app.api.user_films.service import get_a_user_user_film_list

from app.api.auth.hash import hash_password

async def create_user(username: str, password_hash: str, display_name: str, session: AsyncSession = Depends(db_session)):
    result = await session.exec(select(User).where(User.username == username))
    existing = result.first() 
    if existing:
        raise ValueError(f"Username with name {username} already used")
    new_user = User(
        username=username,
        password_hash=password_hash,
        display_name=display_name,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def update_password(id: UUID, new_password: str, session: AsyncSession = Depends(db_session)):
    statement = select(User).where(User.id == id)
    result = await session.exec(statement)
    user = result.one()

    new_hash = hash_password(new_password)
    user.password_hash = new_hash
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

async def get_user_by_id(id: UUID, session: AsyncSession = Depends(db_session)):
    statement = select(User).where(User.id == id)
    result = await session.exec(statement)
    return result.first()

async def get_user_profile(username: str, pagination: dict, from_self: bool, session: AsyncSession = Depends(db_session)):
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()
    if user is None:
        raise ValueError(f"User with username {username} does not exist")
    
    user_films = await get_a_user_user_film_list(user.id, pagination, from_self, session)
    return UserProfile(
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        is_private=user.is_private,
        created_at=user.created_at,
        films=user_films,
    )

async def change_user_password(id: UUID, old_password: str, new_password: str, session: AsyncSession = Depends(db_session)):
    hashed_password = hash_password(old_password)
    statement = select(User).where(User.id == id and User.password_hash == hashed_password)
    result = await session.exec(statement)
    user = result.first()
    if user is None:
        raise ValueError("Old password is incorrect")
    new_hash = hash_password(new_password)
    user.password_hash = new_hash
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

async def update_user_by_id(id: UUID, new_data: UserUpdate, session: AsyncSession = Depends(db_session)):
    statement = select(User).where(User.id == id)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        return None
    
    for field, value in new_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

