from typing import Any, Dict, List, Optional, Tuple

from elasticsearch import Elasticsearch
from sqlalchemy import case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from config import es as es_config
from models.document import Document
from models.paragraph import Paragraph


class ElasticsearchService:
    def __init__(self, db: AsyncSession, account_id: int):
        self.db = db
        self.account_id = account_id
        self.client = Elasticsearch([es_config.host])

    async def find_paragraphs_from_query(
        self,
        question_vector: List[float],
        context_vector: Optional[List[float]],
    ) -> Tuple[List[Paragraph], List[float]]:
        """
        Находим релевантные параграфы в Elasticsearch, а затем получаем их
        объекты из PostgreSQL.
        """

        # Явная типизация для словаря, чтобы избежать путаницы.
        es_query: Dict[str, Any] = {
            "query": {"bool": {"filter": {"term": {"account_id": self.account_id}}}},
            "knn": [
                {
                    "field": "content_vector",
                    "query_vector": question_vector,
                    "k": 64,
                    "num_candidates": 10000,
                    "boost": 0.8,
                }
            ],
        }

        if context_vector:
            es_query["knn"].append(
                {
                    "field": "content_vector",
                    "query_vector": context_vector,
                    "k": 64,
                    "num_candidates": 10000,
                    "boost": 0.2,
                }
            )

        # Выполняем запрос к Elasticsearch
        response = self.client.search(index=es_config.index, body=es_query)

        top_hits = response["hits"]["hits"]
        print("HITS", [{"id": x['_id'], "score": x['_score']} for x in top_hits])

        # Извлекаем id параграфов, у которых score > 0
        ids = [int(x['_id']) for x in top_hits if x['_score'] > 0]
        if not ids:
            return [], []

        # Создаём 'sort_order' для SQLAlchemy, чтобы вернуть параграфы
        # в порядке, соответствующем их позициям в 'ids'
        sort_order = case({id_: index for index, id_ in enumerate(ids)}, value=Paragraph.id)

        # Формируем SQLAlchemy-запрос (переименовали из 'query' в 'stmt')
        stmt = (
            select(Paragraph)
            .options(joinedload(Paragraph.document))
            .join(Document, Paragraph.document_id == Document.id)
            .filter(Paragraph.id.in_(ids), Document.account_id == self.account_id)
            .order_by(sort_order)
        )

        # Асинхронно выполняем запрос
        result = await self.db.execute(stmt)

        # Получаем все результаты запроса
        paragraphs: List[Paragraph] = list(result.scalars().all())
        print("paragraphs", len(paragraphs))

        # Собираем score для каждого параграфа
        scores: List[float] = []
        for p in paragraphs:
            for h in top_hits:
                if p.id == int(h["_id"]):
                    scores.append(h["_score"])

        return paragraphs, scores

    def delete_paragraph(self, paragraph_id: int) -> None:
        """
        Удаляем параграф из Elasticsearch по его ID (в формате str).
        """
        self.client.delete(index=es_config.index, id=str(paragraph_id))
