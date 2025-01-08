from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.sql import functions as func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from middleware.api_middleware import find_account
from models.account import Account
from models.base import document_keyword, paragraph_question
from models.document import Document
from models.keywords import Keyword
from models.paragraph import Paragraph
from services import es as es_service
from services import s3
from services.db.pg_database import get_async_db
from validators.document_requests import CreateDocumentRequest, UpdateDocumentRequest

router = APIRouter(prefix="/documents")


@router.get("")
async def documents_list(
    search: str = "",
    keywords: str = "",
    status: str = "",
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
):
    """
    Возвращает список документов с фильтрацией, пагинацией и агрегацией связанных данных.
    """
    # Подзапрос для подсчета параграфов
    paragraph_subquery = (
        select(Paragraph.document_id, func.count().label("paragraph_count"))
        .group_by(Paragraph.document_id)
        .subquery()
    )

    # Подзапрос для сбора ключевых слов
    keywords_subquery = (
        select(
            document_keyword.c.document_id,
            func.array_agg(Keyword.text).label("keywords"),
        )
        .join(Keyword, document_keyword.c.keyword_id == Keyword.id)
        .group_by(document_keyword.c.document_id)
        .subquery()
    )

    # Основной запрос для фильтрации документов
    base_query = select(Document).where(Document.account_id == account.id)

    # Применение фильтров
    if search:
        base_query = base_query.where(Document.name.ilike(f"%{search}%"))
    if status:
        base_query = base_query.where(Document.status == status.upper())
    if keywords:
        keywords_list = [kw.strip() for kw in keywords.split(",")]
        base_query = (
            base_query.join(document_keyword).join(Keyword).where(Keyword.text.in_(keywords_list))
        )

    # Подсчёт общего количества документов
    total_count = await db.scalar(select(func.count()).select_from(base_query.subquery()))
    pages_count = ((total_count or 0) + limit - 1) // limit

    # Создание запроса с агрегацией
    query = (
        select(
            Document.id,
            Document.name,
            Document.url,
            Document.status,
            Document.created_at,
            Document.updated_at,
            func.coalesce(paragraph_subquery.c.paragraph_count, 0).label("paragraphs_count"),
            func.coalesce(keywords_subquery.c.keywords, []).label("keywords"),
        )
        .outerjoin(paragraph_subquery, Document.id == paragraph_subquery.c.document_id)
        .outerjoin(keywords_subquery, Document.id == keywords_subquery.c.document_id)
        .where(Document.account_id == account.id)
        .order_by(desc(Document.created_at))
        .offset(skip)
        .limit(limit)
    )

    # Выполнение запроса
    result = await db.execute(query)
    rows = result.fetchall()

    # Формирование списка документов
    documents_list = [
        {
            "id": row.id,
            "name": row.name,
            "url": row.url,
            "status": row.status.value if hasattr(row.status, "value") else row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "paragraphs_count": row.paragraphs_count,
            "keywords": row.keywords,
        }
        for row in rows
    ]

    return {
        "documents": documents_list,
        "total_count": total_count,
        "pages_count": pages_count,
    }


@router.post("", status_code=201, tags=["documents"])
async def create_document(
    document_request: CreateDocumentRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
) -> dict[str, Any]:
    """
    Создаёт новый документ, проверяя наличие документа с таким же именем.
    Если существует, возвращает {"document": ..., "created": False}.
    Если не существует, создаёт документ с ключевыми словами и возвращает {"document": ..., "created": True}.
    """
    # Шаг 1: Проверка существования документа с таким же именем
    existing_document = await db.scalar(
        select(Document).where(
            Document.account_id == account.id,
            Document.name == document_request.name,
        )
    )

    if existing_document:
        return {
            "document": {
                "id": existing_document.id,
                "name": existing_document.name,
                "status": existing_document.status,
                "account_id": existing_document.account_id,
                "meta": existing_document.meta,
            },
            "created": False,
        }

    # Шаг 2: Вставка ключевых слов с помощью upsert и сбор их списка
    document_keywords = []
    for kw in document_request.keywords:
        # Вставка ключевого слова через upsert
        insert_stmt = (
            insert(Keyword)
            .values(account_id=account.id, text=kw)
            .on_conflict_do_nothing(index_elements=["text", "account_id"])
        )
        await db.execute(insert_stmt)

        # Загрузка существующего или нового ключевого слова
        keyword = await db.scalar(
            select(Keyword).where(
                Keyword.account_id == account.id,
                Keyword.text == kw,
            )
        )
        if keyword:
            document_keywords.append(keyword)

    # Шаг 3: Создание нового документа
    document = Document(
        url=document_request.url,
        name=document_request.name,
        account_id=account.id,
        meta=document_request.meta,
    )
    document.keywords = document_keywords  # Добавление списка ключевых слов

    # Сохранение документа
    db.add(document)
    await db.commit()
    await db.refresh(document)  # Обновление объекта для получения id и других полей

    # Шаг 4: Логика post-processing (если требуется)
    document.send_to_reader()

    return {
        "document": {
            "id": document.id,
            "name": document.name,
            "status": document.status,
            "account_id": document.account_id,
            "meta": document.meta,
        },
        "created": True,
    }


@router.put("/{item_id}", tags=["documents"])
async def update_item(
    item_id: int,
    document_request: UpdateDocumentRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
) -> Any:
    # Шаг 1. Асинхронно загрузить документ
    document = await db.get(Document, item_id)

    # Шаг 2. Проверить, существует ли документ
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Шаг 3. Проверить доступ пользователя
    if document.account_id != account.id:
        raise HTTPException(status_code=403, detail="Document is out of your scope")

    # Шаг 4. Обновить поля документа
    document.name = document_request.name

    # Шаг 5. Зафиксировать изменения в базе данных
    await db.commit()

    # Шаг 6. Вернуть обновлённый документ
    return {"document": document}


@router.get("/{item_id}", tags=["documents"])
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
):
    # Шаг 1. Собираем подзапрос для агрегации ключевых слов
    keywords_subquery = (
        select(
            document_keyword.c.document_id,
            func.array_agg(Keyword.text).label("keywords"),
        )
        .join(Keyword, document_keyword.c.keyword_id == Keyword.id)
        .group_by(document_keyword.c.document_id)
        .subquery()
    )

    # Шаг 2. Собираем основной запрос на выборку документа + ключевых слов
    #         Обратите внимание: используем select(...) вместо db.query(...).
    document_query = (
        select(Document, func.coalesce(keywords_subquery.c.keywords, []).label("keywords"))
        .join_from(
            Document,
            keywords_subquery,
            Document.id == keywords_subquery.c.document_id,
            isouter=True,
        )
        .options(joinedload(Document.paragraphs))  # подгрузим параграфы
        .where(Document.id == item_id, Document.account_id == account.id)
    )

    # Шаг 3. Выполняем запрос асинхронно
    result = await db.execute(document_query)
    row = result.first()

    # Если ничего не вернулось, выбрасываем 404
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    # row[0] - это Document, row[1] - это список ключевых слов
    document = row[0]
    keywords = row[1] or []  # подстрахуемся на случай None

    response = {
        "id": document.id,
        "name": document.name,
        "status": document.status,
        "url": document.url,
        "account_id": document.account_id,
        "meta": document.meta,
        "paragraphs": document.paragraphs,
        "keywords": keywords,
    }

    return {"document": response}


@router.get("/{item_id}/paragraphs/{paragraph_id}/content", tags=["documents"])
async def get_item_content(
    item_id: int,
    paragraph_id: int,
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
):
    # Загрузка документа с параграфами и тюнами
    document_query = (
        select(Document)
        .options(joinedload(Document.paragraphs))
        .where(Document.id == item_id, Document.account_id == account.id)
    )
    document_result = await db.execute(document_query)
    document = document_result.scalars().first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    paragraph_query = select(Paragraph).where(
        Paragraph.document_id == item_id, Paragraph.id == paragraph_id
    )
    paragraph_result = await db.execute(paragraph_query)
    paragraph = paragraph_result.scalars().first()

    if not paragraph:
        raise HTTPException(status_code=404, detail="Paragraph not found")

    if not paragraph.content_url:
        return {"content": "Paragraph has no content"}

    # Предполагается, что `s3.read_content` асинхронный
    content = s3.read_content(paragraph.content_url)

    return {"content": content}


@router.delete("/{item_id}")
async def delete_document(
    item_id: int,
    db: AsyncSession = Depends(get_async_db),
    account: Account = Depends(find_account),
) -> Any:
    # Получение документа с использованием асинхронного запроса
    result = await db.execute(select(Document).where(Document.id == item_id))
    document = result.scalars().first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.account_id != account.id:
        raise HTTPException(status_code=404, detail="Document is out of your scope")

    # Получение связанных параграфов асинхронно
    paragraphs_result = await db.execute(
        select(Paragraph).where(Paragraph.document_id == document.id)
    )
    paragraphs = paragraphs_result.scalars().all()

    # Инициализация Elasticsearch сервиса
    svc = es_service.ElasticsearchService(db, account.id)

    # Удаление параграфов из Elasticsearch
    for paragraph in paragraphs:
        svc.delete_paragraph(paragraph.id)

    # Удаление записей в таблице paragraph_question
    await db.execute(
        paragraph_question.delete().where(paragraph_question.c.document_id == document.id)
    )

    # Удаление документа
    await db.delete(document)
    await db.commit()

    return {"success": True}
