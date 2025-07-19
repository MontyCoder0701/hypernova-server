from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from controller import auth, schedule
from core.config import DB_URL, FLUTTER_URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FLUTTER_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(schedule.router)

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["model"]},
    add_exception_handlers=True,
    # generate_schemas=True,  # only for dev
)
