from pydantic import BaseModel

from models.settings import SettingsKey


# Создайте Pydantic модель для вашего запроса
class SetSetting(BaseModel):
    key: SettingsKey
    value: str
