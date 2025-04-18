from fastapi import APIRouter

from app.api.genres.router import router as genre_router
from app.api.auth.router import router as auth_router

api_router = APIRouter()

api_router.include_router(genre_router, prefix="/genre")
api_router.include_router(auth_router)
