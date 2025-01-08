from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from models.account import Account
from models.settings import Settings, SettingsKey
from services.db.pg_database import get_db

PUBLIC_ROUTES = ["/api/docs", "/api/openapi.json"]

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def find_account(
    db: Session = Depends(get_db), api_key: str = Security(api_key_header)
) -> Account:
    settings = (
        db.query(Settings)
        .filter(Settings.key == SettingsKey.ACCOUNT_API_KEY, Settings.value == api_key)
        .first()
    )

    if settings is None:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    account: Account | None = db.query(Account).get(settings.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account does not exist")
    return account
