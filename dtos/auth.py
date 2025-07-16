from pydantic import BaseModel


class LoginInput(BaseModel):
    id: str
