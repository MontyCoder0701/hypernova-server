from fastapi import HTTPException, status

from core.auth import create_access_token
from dto.auth import LoginInput


class AuthService:
    def login(self, data: LoginInput) -> dict:
        if data.id != "hypernova":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID"
            )

        token = create_access_token(data={"sub": data.id})
        return {"access_token": token, "token_type": "bearer"}
