import asyncio
from typing import List, Tuple, cast

from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document
from models.paragraph import Paragraph
from models.question import Question
from models.usage_logs import UsageLog
from services import ai as ai_service
from services.ai_clients.interfaces import AIMessage
from services.es import ElasticsearchService
from services.media_processor import MediaProcessor
from services.s3 import StorageService


class DocumentRetriever:
    def __init__(self, db: AsyncSession, question: Question, media_processor: MediaProcessor):
        self.db = db
        self.question = question
        self.embed_client = ai_service.AIService('openai', question.account_id)
        self.media_processor = media_processor
        self.elastic_service = ElasticsearchService(self.db, question.account_id)
        self.storage_service = StorageService()

    async def retrieve_documents(
        self,
        question_files_content: str,
        history_messages: List[AIMessage],
        context: str,
    ) -> Tuple[List[Paragraph], str, List[float]]:
        """Ищет релевантные документы для запроса."""

        history_text = [m.content for m in history_messages]

        context_text = f"{context}\n{history_text}"
        context_vector = None
        if context_text:
            context_vector, usage = await self.get_embeddings(f"{context}\n{history_text}")

        search_pattern = f"{self.question.text}\n{question_files_content}"
        question_vector, usage = await self.get_embeddings(search_pattern)

        paragraphs, scores = await self.elastic_service.find_paragraphs_from_query(
            question_vector=question_vector,
            context_vector=context_vector,
        )

        if len(paragraphs) == 0:
            return [], "", []

        relevant_paragraphs, content = await self.re_rank_paragraphs(search_pattern, paragraphs)
        await self.question.attach_paragraphs(self.db, relevant_paragraphs, scores)

        return relevant_paragraphs, content, scores

    async def get_embeddings(self, text: str):
        """Векторизует текстовый запрос."""
        vector, usage = await self.embed_client.embed(text)
        await UsageLog.log_async(
            self.db,
            {
                "account_id": self.question.account_id,
                "source_key": "question",
                "source_id": self.question.id,
                "operation": "answer",
                "embedding": usage.output_tokens,
            },
            usage.model_name,
        )
        return vector, usage

    async def re_rank_paragraphs(
        self, input_text: str, paragraphs: List[Paragraph]
    ) -> Tuple[List[Paragraph], str]:
        if not self.embed_client.embedder:
            raise ValueError("EmbedClient is not initialized")

        context_text = ""
        tasks = []

        for p in paragraphs:
            if not p.content_url:
                continue
            task = asyncio.to_thread(self.storage_service.read_content, p.content_url)
            tasks.append(task)

        contents = await asyncio.gather(*tasks)

        sorts, scores, re_rank_usage = self.embed_client.embedder.re_rank(
            input_text, [c[0] for c in contents]
        )

        relevant_paragraphs = []
        for idx in sorts:
            sorted_paragraphs: Paragraph = paragraphs[idx]
            await self.db.refresh(sorted_paragraphs)  # todo: выглядит плохо

            document: Document = cast(Document, sorted_paragraphs.document)
            document_meta = document.meta
            if document_meta:
                context_text = context_text + f"Source:{document_meta}\n\nContent:\n"
            context_text += contents[idx]

            relevant_paragraphs.append(p)

        await UsageLog.log_async(
            self.db,
            {
                "account_id": self.question.account_id,
                "source_key": "question",
                "source_id": self.question.id,
                "operation": "re_rank",
                "input": re_rank_usage.input_tokens,
                "output": re_rank_usage.output_tokens,
            },
            re_rank_usage.model_name,
        )

        return relevant_paragraphs, context_text
