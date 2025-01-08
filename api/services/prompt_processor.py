from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.question import Question
from models.settings import get_prompt_template
from services.ai_clients.interfaces import AIMessage


class PromptProcessor:
    def __init__(self, db: AsyncSession, account_id: int):
        self.db = db
        self.account_id = account_id

    async def process_prompt(
        self,
        question: Question,
        question_files_content: str,
        history_messages: List[AIMessage],
    ) -> List[AIMessage]:
        """Создает список сообщений для LLM."""

        template = await self.get_template()
        prompt = template.replace("{{prompt}}", f"{question_files_content}\n{question.text}")
        return [*history_messages, AIMessage(role="user", content=prompt)]

    async def get_template(self) -> str:
        """Получает шаблон промпта для текущего аккаунта."""
        return await get_prompt_template(self.db, self.account_id)
