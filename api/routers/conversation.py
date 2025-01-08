from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Session

from middleware.api_middleware import find_account
from models.account import Account
from models.conversation import Conversation
from services.db.pg_database import get_db

router = APIRouter(prefix="/conversations")


@router.get("", status_code=200, tags=["conversations"])
async def get_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    account: Account = Depends(find_account),
):
    # Начало запроса
    query = db.query(Conversation).filter(Conversation.account_id == account.id)

    total_count = query.with_entities(func.count(Conversation.id)).scalar()
    pages_count = (total_count + limit - 1) // limit

    # Сортировка по убыванию даты создания лога и пагинация
    conversations = query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()

    return {
        "conversations": conversations,
        "total_count": total_count,
        "pages_count": pages_count,
    }
