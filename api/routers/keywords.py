from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from middleware.api_middleware import find_account
from models.account import Account
from models.keywords import Keyword
from services.db.pg_database import get_db

router = APIRouter(prefix="/keywords")


@router.get("", status_code=200, tags=["usage"])
async def get_keywords(
    search: str = "",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    account: Account = Depends(find_account),
):
    # Начало запроса
    query = db.query(Keyword).filter(Keyword.account_id == account.id)

    if search:
        query = query.filter(Keyword.text.ilike(f"%{search}%"))

    keywords = query.offset(skip).limit(limit).all()

    return {
        "keywords": keywords,
    }
