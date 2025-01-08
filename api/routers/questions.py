from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.sql import functions as func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload, subqueryload

from controllers import question_controller
from middleware.api_middleware import find_account
from models.account import Account
from models.conversation import Conversation
from models.paragraph import Paragraph
from models.question import Question
from services.answer_generator import AnswerGenerator
from services.db.pg_database import get_async_db, get_db
from validators.question_requests import CreateQuestionRequest

router = APIRouter(prefix="/questions")


@router.get("", status_code=200, tags=["questions"])
async def get_questions(
        skip: Optional[int] = 0,
        limit: Optional[int] = 10,
        reaction: Optional[str] = None,
        model_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        db: Session = Depends(get_db),
        account: Account = Depends(find_account),
):
    # Основной запрос
    base_query = db.query(Question).filter(Question.account_id == account.id)

    # Применение фильтров
    if conversation_id:
        base_query = base_query.filter(Question.conversation_id == conversation_id)
    else:
        base_query = base_query.filter(Question.conversation_id.is_(None))
    if reaction:
        base_query = base_query.filter(Question.reaction == reaction)
    if model_id:
        base_query = base_query.filter(Question.model_id == model_id)
    if date_from:
        base_query = base_query.filter(Question.created_at >= date_from)
    if date_to:
        base_query = base_query.filter(Question.created_at <= date_to)

    # Вычисление общего количества вопросов
    total_count = base_query.with_entities(func.count(Question.id)).scalar()
    # Вычисление количества страниц
    if not limit:
        limit = 10

    pages_count = (total_count + limit - 1) // limit

    # Получение и сериализация вопросов с учетом сортировки и пагинации
    questions = (
        base_query.order_by(desc(Question.created_at))
        .options(
            joinedload(Question.model),
            subqueryload(Question.question_files),
            subqueryload(Question.paragraphs).joinedload(Paragraph.document),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "questions": questions,
        "total_count": total_count,
        "pages_count": pages_count,
    }


@router.post("", status_code=200, tags=["questions"])
async def create_question(
        request: CreateQuestionRequest = Body(...),
        db: AsyncSession = Depends(get_async_db),
        account: Account = Depends(find_account),
):
    conversation = await Conversation.find_or_create(
        db, account.id, request.conversation_id, request.text
    )
    conversation.updated_at = datetime.now()

    question = await question_controller.create_question_record(db, account, request, conversation)

    if request.files:
        await question_controller.save_question_files(db, question, request.files)

    generator = AnswerGenerator(
        question=question,
        context=request.context,
        db=db,
        stream=request.stream,
        webhook=request.webhook,
        tools=request.tools,
    )
    return await generator.generate_answer()


@router.get("/{item_id}", status_code=200, tags=["questions"])
async def get_question(
        item_id: int,
        db: Session = Depends(get_db),
        account: Account = Depends(find_account),
):
    # Основной запрос
    base_query = db.query(Question).filter(
        Question.account_id == account.id, Question.id == item_id
    )

    # Получение и сериализация вопросов с учетом сортировки и пагинации
    question = (
        base_query.order_by(desc(Question.created_at))
        .options(
            joinedload(Question.model),
            subqueryload(Question.paragraphs).joinedload(Paragraph.document),
        )
        .first()
    )

    if not question:
        raise HTTPException(404, "Question not found")

    return {
        "question": question,
    }


@router.post("/{item_id}/like", tags=["questions"])
async def like(
        item_id: int,
        db: Session = Depends(get_db),
        account: Account = Depends(find_account),
):
    question = db.get(Question, item_id)
    if not question:
        raise HTTPException(404, "Question not found")

    if question.account_id != account.id:
        raise HTTPException(401, "Question is out of your scope")
    question.reaction = "like"
    question.reacted_at = datetime.now()
    db.commit()
    db.refresh(question)

    return {"question": question}


@router.post("/{item_id}/dislike", tags=["questions"])
async def dislike(
        item_id: int,
        db: Session = Depends(get_db),
        account: Account = Depends(find_account),
):
    question = db.get(Question, item_id)
    if not question:
        raise HTTPException(404, "Question not found")

    if question.account_id != account.id:
        raise HTTPException(401, "Question is out of your scope")
    question.reaction = "dislike"
    question.reacted_at = datetime.now()
    db.commit()
    db.refresh(question)

    return {"question": question}
