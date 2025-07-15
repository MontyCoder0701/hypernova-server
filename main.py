from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from tortoise.contrib.fastapi import register_tortoise
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

import os
from datetime import date
from typing import List

from models.schedule import Schedule

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


## TODO: 메서드, 클래스, 엔드포인트 main에서 전부 분리
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != "hypernova":
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return "hypernova"


class ScheduleIn(BaseModel):
    days: List[str] = Field(..., example=["월", "수", "금"])
    time: str = Field(..., example="14:00:00")
    is_active: bool = True
    start_date: date


class ScheduleOut(ScheduleIn):
    id: int
    days: List[str] = Field(..., example=["월", "수", "금"])
    time: str = Field(..., example="14:00:00")
    is_active: bool = True
    start_date: date


@app.post("/token")
def login():
    access_token = create_access_token(data={"sub": "hypernova"})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/schedules", response_model=List[ScheduleOut])
async def read_schedules(user: str = Depends(get_current_user)):
    schedules = await Schedule.all()
    return schedules


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models.schedule"]},
    add_exception_handlers=True,
    ## WARN: Disable in production
    # generate_schemas=True,
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
