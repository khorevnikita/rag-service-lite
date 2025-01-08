from pydantic import BaseModel


# Создайте Pydantic модель для вашего запроса
class DownloadRequest(BaseModel):
    path: str
