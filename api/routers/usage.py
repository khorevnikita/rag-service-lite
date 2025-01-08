from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Session

from middleware.api_middleware import find_account
from models.account import Account
from models.usage_logs import UsageLog
from services.db.pg_database import get_db

router = APIRouter(prefix="/usage")


@router.get("", status_code=200, tags=["usage"])
async def get_usage_logs(
    skip: Optional[int] = 0,
    limit: Optional[int] = 10,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    operation: Optional[str] = None,
    document_id: Optional[int] = None,
    db: Session = Depends(get_db),
    account: Account = Depends(find_account),
):
    # Начало запроса
    query = db.query(UsageLog).filter(UsageLog.account_id == account.id)

    # Фильтрация по диапазону дат
    if date_from:
        query = query.filter(UsageLog.created_at >= date_from)
    if date_to:
        query = query.filter(UsageLog.created_at <= date_to)

    # Фильтрация по операции
    if operation:
        query = query.filter(UsageLog.operation == operation)

    total_count = query.with_entities(func.count(UsageLog.id)).scalar()
    pages_count = (total_count + limit - 1) // limit

    # Сортировка по убыванию даты создания лога и пагинация
    logs = query.order_by(desc(UsageLog.created_at)).offset(skip).limit(limit).all()

    return {"usage_logs": logs, "total_count": total_count, "pages_count": pages_count}
