from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.model import Model
from models.question import Question
from models.usage_logs import UsageLog
from services.ai import AIService
from services.ai_clients.interfaces import AIMessage, UsageData
from validators.question_requests import FunctionDefinition


class AnswerHandler:
    def __init__(
            self,
            ai_client: AIService,
            db: AsyncSession,
            question: Question,
            tools: Optional[List[FunctionDefinition]],
    ):
        self.ai_client = ai_client
        self.db = db
        self.question = question
        self.tools = tools

    async def generate_streaming_response(
            self, context: str, messages: List[AIMessage]
    ) -> StreamingResponse:
        """Генерирует ответ в режиме стрима."""
        background_tasks = BackgroundTasks()

        def stream_response() -> AsyncGenerator[str, None]:
            """Асинхронный генератор для передачи данных стрима."""
            full_reply_content = ""
            usage = None

            for chunk, current_usage in self.ai_client.create_message_stream(context, messages):
                # Собираем полный ответ
                full_reply_content += chunk
                # Отправляем текущий кусок текста клиенту
                yield chunk
                # Если это последний кусок, сохраняем usage
                usage = current_usage

            # Сохраняем полный ответ в БД
            if usage:
                background_tasks.add_task(
                    self.save_answer, usage.model_name, full_reply_content, None
                )
                background_tasks.add_task(self.log_usage, usage)

        headers: dict[str, str] = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "question-id": str(self.question.id),
            "conversation-id": str(self.question.conversation_id),
        }
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers=headers,
            background=background_tasks,
        )

    async def generate_sync_answer(
            self, context: str, messages: List[AIMessage]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Генерирует синхронный ответ.
        """
        answer, audio_file, tools_called, usage = await self.ai_client.create_message(
            context, messages, self.tools, self.question.answer_format
        )

        await self.save_answer(usage.model_name, str(answer), audio_file, tools_called)
        await self.log_usage(usage)

        return answer, tools_called

    async def save_answer(
            self, model_name: str, answer: str, audio_file: Optional[str] = None,
            called_tools: Optional[List[Dict[str, Any]]] = None
    ):
        # Находим данные о модели
        query = select(Model).where(Model.base_model_name == model_name)
        result = await self.db.execute(query)
        model = result.scalars().first()
        if not model:
            return

        self.question = await self.db.merge(self.question)
        self.question.model_id = model.id
        self.question.answer = answer
        self.question.audio_file = audio_file
        self.question.answered_at = datetime.now()
        self.question.called_tools = called_tools
        await self.db.commit()

    async def log_usage(self, usage: UsageData):
        """Логирует использование модели."""
        await UsageLog.log_async(
            self.db,
            {
                "account_id": self.question.account_id,
                "source_key": "question",
                "source_id": self.question.id,
                "operation": "answer",
                "input": usage.input_tokens,
                "output": usage.output_tokens,
            },
            usage.model_name,
        )
