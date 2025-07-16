from fastapi import FastAPI, Depends, HTTPException, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from tortoise.contrib.fastapi import register_tortoise
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

import os
from datetime import date, timedelta
from typing import List

from models import User, Schedule

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
def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    username = verify_token(token)
    user = await User.get_or_none(username=username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


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

    @classmethod
    def from_orm(cls, obj: Schedule) -> "ScheduleOut":
        td: timedelta = obj.time
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        return cls(
            id=obj.id,
            days=obj.days,
            time=time_str,
            is_active=obj.is_active,
            start_date=obj.start_date,
        )


class LoginInput(BaseModel):
    id: str


@app.post("/token")
def login(data: LoginInput) -> dict[str, str]:
    if data.id != "hypernova":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID"
        )

    access_token = create_access_token(data={"sub": data.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/schedules", response_model=List[ScheduleOut])
async def get_schedules(user: User = Depends(get_current_user)):
    schedules = await Schedule.filter(user=user)
    return [ScheduleOut.from_orm(s) for s in schedules]


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]},
    add_exception_handlers=True,
    ## WARN: Disable in production
    # generate_schemas=True,
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
