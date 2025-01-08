from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.settings import get_context_template
from services.ai_clients.interfaces import AIMessage
from services.document_retriever import DocumentRetriever


class ContextBuilder:
    def __init__(
        self,
        db: AsyncSession,
        account_id: int,
        client_context: Optional[str],
        document_retriever: DocumentRetriever,
    ):
        self.db = db
        self.account_id = account_id
        self.client_context = client_context
        self.document_retriever = document_retriever

    async def build_context(
        self, question_files_content: str, history_messages: List[AIMessage]
    ) -> str:
        """Создает контекст для запроса."""
        context_template = await get_context_template(self.db, self.account_id)

        # Поиск релевантных документов
        paragraphs, document_content, scores = await self.document_retriever.retrieve_documents(
            question_files_content=question_files_content,
            history_messages=history_messages,
            context=context_template,
        )

        return context_template.replace(
            "{{context}}",
            f"{self.client_context if self.client_context else ''}\n\n{document_content}",
        )
