from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from middleware.api_middleware import find_account
from models.account import Account
from models.settings import Settings
from services.db.pg_database import get_db
from validators.settings_requests import SetSetting

from services.s3 import upload
router = APIRouter(prefix="/settings")


@router.get("", status_code=200, tags=["settings"])
async def get_settings(db: Session = Depends(get_db), account: Account = Depends(find_account)):
    # Начало запроса
    settings = db.query(Settings).filter(Settings.account_id == account.id).all()
    return {
        "settings": settings,
    }


@router.post("", status_code=200, tags=["settings"])
async def set_settings(
    request: SetSetting = Body(...),
    db: Session = Depends(get_db),
    account: Account = Depends(find_account),
):
    # Начало запроса
    settings = (
        db.query(Settings)
        .filter(Settings.account_id == account.id, Settings.key == request.key)
        .first()
    )
    if not settings:
        # create settings
        settings = Settings(key=request.key, value=request.value, account_id=account.id)
        db.add(settings)
    else:
        settings.value = request.value
    db.commit()
    db.refresh(settings)
    return {
        "settings": settings,
    }
