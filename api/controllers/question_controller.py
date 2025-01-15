from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.question import Question
from models.question_file import QuestionFile
from services import file as file_service
from validators.question_requests import CreateQuestionRequest, FileItem


async def create_question_record(
        db: AsyncSession,
        account,
        request: CreateQuestionRequest,
        conversation,
) -> Question:  # media
    """Создает запись вопроса в базе данных."""
    question = Question(
        text=request.text,
        account_id=account.id,
        conversation_id=conversation.id,
        available_tools=[i.to_dict() for i in request.tools] if request.tools else None,
        answer_format=request.answer_format.value,
    )
    db.add(question)
    await db.commit()
    return question


async def save_question_files(db: AsyncSession, question: Question, files: List[FileItem]):
    """Создает информацию о файлах вопроса в базе данных."""
    for f in files:
        file = QuestionFile(
            conversation_id=question.conversation_id,
            question_id=question.id,
            url=f.file_path,
            name=f.filename,
            size=f.size,
            extension=f.extension,
            type=file_service.get_type(f.file_path),
            is_private=file_service.is_private(f.file_path),
        )
        db.add(file)

    await db.commit()
