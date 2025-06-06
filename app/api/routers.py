from fastapi import APIRouter

from app.api.genres.router import router as genre_router
from app.api.auth.router import router as auth_router
from app.api.users.router import router as user_router
from app.api.films.router import router as film_router
from app.api.user_films.router import router as user_film_router
from app.api.reviews.router import router as review_router

api_router = APIRouter()

api_router.include_router(genre_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(film_router)
api_router.include_router(user_film_router)
api_router.include_router(review_router)