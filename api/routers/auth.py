from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from models.account import Account
from models.settings import Settings, SettingsKey
from services.db.pg_database import get_db

router = APIRouter(prefix="/auth")


@router.get("/me")
async def get_me(
    db: Session = Depends(get_db), session: SessionContainer = Depends(verify_session())
):
    user_id = session.get_user_id()

    account = db.query(Account).filter(Account.supertokens_id == user_id).first()
    if not account:
        raise HTTPException(401, f"Account does not exist")

    settings = (
        db.query(Settings)
        .filter(Settings.account_id == account.id, Settings.key == SettingsKey.ACCOUNT_API_KEY)
        .first()
    )
    if not settings:
        raise HTTPException(401, f"Settings does not exist")

    return {
        "account": {
            "id": account.id,
            "login": account.login,
            "is_active": account.is_active,
        },
        "settings": settings,
    }
