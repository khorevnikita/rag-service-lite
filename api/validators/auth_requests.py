from pydantic import BaseModel


# Создайте Pydantic модель для вашего запроса
class LoginRequest(BaseModel):
    login: str
    password: str


class TokenRequest(BaseModel):
    code: str
