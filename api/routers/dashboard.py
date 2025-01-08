from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from middleware.api_middleware import find_account
from models.account import Account
from models.base import document_keyword
from models.conversation import Conversation
from models.document import Document
from models.keywords import Keyword
from models.question import Question
from models.usage_logs import UsageLog
from services.db.pg_database import get_db

router = APIRouter(prefix="/dashboard")


@router.get("", status_code=200, tags=["dashboard"])
async def get_dashboard_data(
        db: Session = Depends(get_db), account: Account = Depends(find_account)
):
    # Количество вопросов
    total_questions = db.query(Question).filter(Question.account_id == account.id).count()
    total_conversations = (
        db.query(Conversation).filter(Conversation.account_id == account.id).count()
    )

    # Количество вопросов с различными реакциями
    likes_count = (
        db.query(Question)
        .filter(Question.reaction == "like", Question.account_id == account.id)
        .count()
    )
    dislikes_count = (
        db.query(Question)
        .filter(Question.reaction == "dislike", Question.account_id == account.id)
        .count()
    )

    # Количество документов
    total_documents = db.query(Document).filter(Document.account_id == account.id).count()

    # Распределение документов по статусам
    document_status_distribution = (
        db.query(Document.status, functions.count(Document.id))
        .filter(Document.account_id == account.id)
        .group_by(Document.status)
        .all()
    )

    # Суммарное количество потраченных токенов
    spent_total = (
        db.query(functions.sum(UsageLog.price)).filter(UsageLog.account_id == account.id).scalar()
    )

    # Суммарное количество токенов за текущий месяц
    now = datetime.now()
    start_current_month = datetime(now.year, now.month, 1)
    spent_current_month = (
        db.query(functions.sum(UsageLog.price))
        .filter(
            UsageLog.created_at >= start_current_month,
            UsageLog.account_id == account.id,
        )
        .scalar()
    )

    # Суммарное количество токенов за прошлый месяц
    start_last_month = start_current_month - timedelta(days=1)
    start_last_month = datetime(start_last_month.year, start_last_month.month, 1)
    spent_previous_month = (
        db.query(functions.sum(UsageLog.price))
        .filter(
            UsageLog.created_at >= start_last_month,
            UsageLog.created_at < start_current_month,
            UsageLog.account_id == account.id,
        )
        .scalar()
    )

    # Предполагаем, что `Conversation.created_at` - это поле с датой создания
    start_date = datetime.now() - timedelta(days=30)

    # Определение CTE для начального количества
    initial_count_cte = (
        select(functions.count().label('count'))
        .where(Conversation.account_id == account.id, Conversation.created_at < start_date)
        .cte('initial_count')
    )

    # Определение CTE для дневных подсчётов
    daily_counts_cte = (
        select(
            func.date(Conversation.created_at).label('date'),
            functions.count().label('daily_count'),
        )
        .where(Conversation.account_id == account.id, Conversation.created_at >= start_date)
        .group_by(func.date(Conversation.created_at))
        .cte('daily_counts')
    )

    # Итоговый запрос, объединяющий CTE
    final_query = select(
        daily_counts_cte.c.date,
        (
                select(initial_count_cte.c.count)
                + functions.sum(daily_counts_cte.c.daily_count).over(order_by=daily_counts_cte.c.date)
        ).label('cumulative_count'),
    ).select_from(daily_counts_cte)

    # Выполнение запроса
    result = db.execute(final_query).fetchall()

    # Преобразование результатов в желаемый формат
    conversations_on_day = [
        {'date': row[0], 'count': row[1]} for row in result if isinstance(row, (list, tuple))
    ]

    total_questions_per_day = (
        db.query(
            func.date(Question.created_at).label('date'),
            functions.count(Question.id).label('count'),
        )
        .filter(Question.account_id == account.id, Question.created_at >= start_date)
        .group_by(func.date(Question.created_at))
        .order_by('date')
        .all()
    )
    total_questions_per_day = [{'date': x[0], 'count': x[1]} for x in total_questions_per_day]
    like_questions_per_day = (
        db.query(
            func.date(Question.created_at).label('date'),
            functions.count(Question.id).label('count'),
        )
        .filter(
            Question.account_id == account.id,
            Question.created_at >= start_date,
            Question.reaction == "like",
        )
        .group_by(func.date(Question.created_at))
        .order_by('date')
        .all()
    )
    like_questions_per_day = [{'date': x[0], 'count': x[1]} for x in like_questions_per_day]

    dislike_questions_per_day = (
        db.query(
            func.date(Question.created_at).label('date'),
            functions.count(Question.id).label('count'),
        )
        .filter(
            Question.account_id == account.id,
            Question.created_at >= start_date,
            Question.reaction == "dislike",
        )
        .group_by(func.date(Question.created_at))
        .order_by('date')
        .all()
    )
    dislike_questions_per_day = [{'date': x[0], 'count': x[1]} for x in dislike_questions_per_day]

    usage_per_day = (
        db.query(
            func.date(UsageLog.created_at).label('date'),
            functions.sum(UsageLog.price).label('count'),
        )
        .filter(UsageLog.account_id == account.id, UsageLog.created_at >= start_date)
        .group_by(func.date(UsageLog.created_at))
        .order_by('date')
        .all()
    )
    usage_per_day = [{'date': x[0], 'sum': round(x[1], 2)} for x in usage_per_day]

    stmt = (
        select(
            Keyword.id,
            Keyword.text,
            functions.count(document_keyword.c.document_id).label('count'),
        )
        .join_from(Keyword, document_keyword, Keyword.id == document_keyword.c.keyword_id)
        .filter(Keyword.account_id == account.id)
        .group_by(Keyword.id)
        .order_by(functions.count(document_keyword.c.document_id).desc())
    )

    keyword_distribution = db.execute(stmt).fetchall()
    keyword_distribution = [
        {"id": x[0], "text": x[1], "count": x[2]}
        for x in keyword_distribution
        if isinstance(x, tuple)
    ]

    return {
        "total_conversations": total_conversations or 0,
        "total_questions": total_questions or 0,
        "likes_count": likes_count or 0,
        "dislikes_count": dislikes_count or 0,
        "total_documents": total_documents or 0,
        "document_status_distribution": [
            dict(status=x[0], count=x[1]) for x in document_status_distribution
        ],
        "spent_total": spent_total or 0,
        "spent_current_month": spent_current_month or 0,
        "spent_previous_month": spent_previous_month or 0,
        "conversations_on_day": conversations_on_day,
        "total_questions_per_day": total_questions_per_day,
        "like_questions_per_day": like_questions_per_day,
        "dislike_questions_per_day": dislike_questions_per_day,
        "usage_per_day": usage_per_day,
        "keyword_distribution": keyword_distribution,
    }
