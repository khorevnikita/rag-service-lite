from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.question import Question
from models.question_file import QuestionFile
from models.usage_logs import UsageLog
from services import file as file_service
from services import reader as file_reader
from services import s3
from services.reader import MediaSource


class MediaProcessor:
    def __init__(self, db: AsyncSession, question: Question):
        self.db = db
        self.question = question

    async def process_unknown(self, file: QuestionFile) -> str:
        """Обрабатывает неизвестные файлы и извлекает текстовое содержимое."""
        if file_service.is_private(file.url):
            local_path = s3.download(file.url)
        else:
            local_path = file_service.download(file.url)

        reader = file_reader.Reader(local_path, self.question.account_id)
        description = await reader.get_content_async()
        file_service.delete_file(local_path)
        if description:
            return f'File: {file.name}:\nContent:{description}\n\n'
        return ""

    async def process_pdf(self, pdf: QuestionFile) -> str:
        """Обрабатывает PDF-файл и извлекает текстовое содержимое."""
        if file_service.is_private(pdf.url):
            local_path = s3.download(pdf.url)
        else:
            local_path = file_service.download(pdf.url)

        reader = file_reader.Reader(local_path, self.question.account_id)
        description = await reader.get_content_async()
        if not description:
            return ""
        content = description.strip()
        file_service.delete_file(local_path)
        if len(content) > 0:
            return f'File: {pdf.name}:\nContent:{content}\n\n'
        return ""

    async def process_images(self, files: List[QuestionFile]) -> str:
        """Обрабатывает изображения и извлекает текст через OCR."""
        media_sources = []
        for f in files:
            if file_service.is_pdf(f.url):
                image_pages = await file_reader.pdf_to_image(f)
                media_sources.extend(image_pages)
            else:
                media_sources.append(
                    MediaSource(
                        url=f.url,
                        name=f.name,
                        extension=f.extension,
                        is_private=f.is_private,
                    )
                )

        vision = file_reader.Vision(self.question.account_id, media_sources)
        description, usage = await vision.get_content()

        await UsageLog.log_async(
            self.db,
            {
                "account_id": self.question.account_id,
                "source_key": "question",
                "source_id": self.question.id,
                "operation": "ocr",
                "input": usage.input_tokens,
                "output": usage.output_tokens,
            },
            usage.model_name,
        )
        content: str = description.strip()
        if len(content) > 0:
            return content
        return ""

    async def process_audio(self, audio: MediaSource) -> str:
        """Обрабатывает аудио-файл и извлекает текст."""
        whisper = file_reader.Whisper(self.question.account_id, [audio])
        description, usage = await whisper.get_content()

        await UsageLog.log_async(
            self.db,
            {
                "account_id": self.question.account_id,
                "source_key": "question",
                "source_id": self.question.id,
                "operation": "voice_to_text",
                "input": usage.input_tokens,
                "output": usage.output_tokens,
            },
            usage.model_name,
        )

        text: str = description.strip()
        return text
