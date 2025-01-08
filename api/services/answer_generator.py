from typing import Any, Dict, List, Optional, Union

from fastapi.responses import StreamingResponse
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.question import Question
from models.question_file import QuestionFile
from models.settings import get_generative_provider
from services import ai as ai_service
from services.ai_clients.interfaces import AIMessage
from services.answer_handler import AnswerHandler
from services.context_builder import ContextBuilder
from services.document_retriever import DocumentRetriever
from services.kafka import producer
from services.media_processor import MediaProcessor
from services.prompt_processor import PromptProcessor
from services.reader import MediaSource
from validators.question_requests import FunctionDefinition


class AnswerGenerator:
    def __init__(
        self,
        question: Question,
        context: Optional[str],
        db: AsyncSession,
        stream: bool,
        webhook: Optional[str],
        tools: Optional[List[FunctionDefinition]],
    ):
        self.stream = stream
        self.webhook = webhook
        self.message_history_length = 5
        self.question = question
        self.context = context
        self.db = db
        self.media_processor = MediaProcessor(db, question)
        self.document_retriever = DocumentRetriever(db, question, self.media_processor)
        self.context_builder = ContextBuilder(
            db, question.account_id, context, self.document_retriever
        )
        self.prompt_processor = PromptProcessor(db, question.account_id)

        ai_provider = ai_service.AIService(
            get_generative_provider(question.account_id), question.account_id
        )
        self.answer_handler = AnswerHandler(ai_provider, db, self.question, tools)

    async def generate_answer(self) -> Union[Dict[str, Any], StreamingResponse]:
        # Обработка файлов
        question_files_content = await self.get_question_files_content()

        # Загрузка истории сообщений
        history_messages = await self.load_message_history()

        # Построение контекста
        context = await self.context_builder.build_context(
            question_files_content=question_files_content,
            history_messages=history_messages,
        )

        # Обработка промпта
        messages = await self.prompt_processor.process_prompt(
            question=self.question,
            question_files_content=question_files_content,
            history_messages=history_messages,
        )

        # Генерация ответа
        if self.stream:
            return await self.answer_handler.generate_streaming_response(context, messages)

        await self.answer_handler.generate_sync_answer(context, messages)
        await self.db.refresh(self.question)
        if self.webhook:
            producer.send_message(
                'api',
                'hook_answer',
                f'question_{self.question.id}',
                {
                    "id": self.question.id,
                    "webhook": self.webhook,
                    "context": self.context,
                },
            )
        return {"status": "success", "question": self.question}

    async def load_message_history(self) -> List[AIMessage]:
        # Создаем запрос с использованием select и настройкой фильтров и сортировки
        query = (
            select(Question)
            .where(
                (Question.conversation_id == self.question.conversation_id)
                & (Question.id != self.question.id)
                & (Question.answered_at.isnot(None))
                & (Question.answer != "")
            )
            .order_by(desc(Question.created_at))
            .options(selectinload(Question.question_files))  # Предзагрузка связанных файлов
            .offset(0)
            .limit(self.message_history_length)
        )

        # Выполняем запрос асинхронно
        result = await self.db.execute(query)

        # Получаем все результаты запроса
        prev_questions: List[Question] = list(result.scalars().all())

        prev_questions.reverse()

        history: List[AIMessage] = []
        for question in prev_questions:
            user_content = ""
            if question.question_files:
                # Добавляем содержимое всех связанных файлов к тексту вопроса
                file_contents = "\n".join(
                    file.content for file in question.question_files if file.content
                )
                if file_contents:
                    user_content += f"\n\n[Files:]\n{file_contents}\n"
            user_content += question.text or ""
            history.append(
                AIMessage(
                    role="user",
                    content=user_content,
                ),
            )
            if question.answer:
                history.append(
                    AIMessage(
                        role="assistant",
                        content=question.answer,
                    ),
                )
        return history

    async def get_question_files_content(self) -> str:
        """Извлекает содержимое файлов вопроса для использования в
        контексте."""
        files = await self._get_question_files(self.question.id)
        if not files:
            return ""

        # Определяем корректный тип для files_by_type
        files_by_type: Dict[str, List[QuestionFile]] = {
            'pdf': [],
            'image': [],
            'audio': [],
            'other': [],
        }
        for f in files:
            if f.type in files_by_type:
                files_by_type[f.type].append(f)

        context = ""
        for pdf in files_by_type['pdf']:
            f_content = await self.media_processor.process_pdf(pdf)
            if len(f_content) == 0:
                f_content = await self.media_processor.process_images([pdf])

            context += f"\n{f_content}\n"
            pdf.content = f_content

        if files_by_type['image']:
            image_contents = await self.media_processor.process_images(files_by_type['image'])
            if len(image_contents) > 0:
                context += f"\n{image_contents}\n"
                files_by_type['image'][
                    0
                ].content = image_contents  # тут сохраняем контент в первое изображение из всех

        for audio in files_by_type['audio']:
            media_source = MediaSource(
                url=audio.url,
                name=audio.name,
                extension=audio.extension,
                is_private=audio.is_private,
            )
            audio_content = await self.media_processor.process_audio(media_source)
            if len(audio_content) > 0:
                context += f"\n{audio_content}\n"
                audio.content = audio_content

        for other_file in files_by_type['other']:
            other_content = await self.media_processor.process_unknown(other_file)
            if len(other_content) > 0:
                context += f"\n{other_content}\n"
                other_file.content = other_content

        await self.db.commit()  # Сохраняем содержимое файлов
        return context

    async def _get_question_files(self, question_id: int) -> List[QuestionFile]:
        """Получает файлы, связанные с вопросом."""
        query = select(QuestionFile).where(QuestionFile.question_id == question_id)
        result = await self.db.execute(query)
        files: List[QuestionFile] = list(result.scalars().all())
        return files
