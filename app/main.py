from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from decouple import config

from app.api.routers import api_router

IMAGE_PATH = config("IMAGE_PATH")
app = FastAPI()

app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")