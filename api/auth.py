from fastapi import APIRouter, HTTPException, status

from core.auth import create_access_token
from dtos.auth import LoginInput

router = APIRouter()


@router.post("/token")
def login(data: LoginInput):
    if data.id != "hypernova":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID"
        )
    access_token = create_access_token(data={"sub": data.id})
    return {"access_token": access_token, "token_type": "bearer"}
