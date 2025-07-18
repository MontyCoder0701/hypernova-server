from fastapi import APIRouter, Depends

from dto.auth import LoginInput
from service.auth import AuthService

router = APIRouter()


@router.post("/token")
def login(
    data: LoginInput,
    service: AuthService = Depends(),
):
    return service.login(data)
