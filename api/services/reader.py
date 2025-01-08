import asyncio
import os
from typing import List, Optional, Tuple

import fitz
from pdf2image import convert_from_path

from config.ai import AI_PROVIDER
from models.question_file import QuestionFile
from services import ai, file, s3
from services.ai_clients.interfaces import UsageData


class MediaSource:
    def __init__(self, url: str, name: str, extension: str, is_private: bool):
        self.url = url
        self.name = name
        self.extension = extension
        self.is_private = is_private


async def pdf_to_image(pdf: QuestionFile) -> List[MediaSource]:
    local_path = f'storage/{pdf.id}.pdf'
    images = []

    async with s3.get_async_client() as client:
        # Decide download method based on privacy settings of the PDF
        download_func = s3.download_async if pdf.is_private else file.download_async
        await download_func(pdf.url, local_path)

        # Convert PDF pages to images asynchronously
        pages = await asyncio.to_thread(convert_from_path, local_path, fmt='png', size=2000)

        for i, page in enumerate(pages):
            file_name = f'page-{i}.png'
            directory_path = f'storage/{pdf.id}'
            page_path = f'{directory_path}/{file_name}'

            # Ensure the directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Use a standard synchronous file operation inside a thread for compatibility with PIL
            await asyncio.to_thread(file.save_image, page, page_path)

            remote_path = f'ocr/{pdf.id}/{file_name}'
            await s3.upload_async(client=client, local_path=page_path, remote_path=remote_path)
            images.append(
                MediaSource(
                    url=remote_path,
                    name=pdf.name,
                    extension='png',
                    is_private=True,
                )
            )

            # Optional cleanup step if you don't need the local copies after processing
            os.remove(page_path)

    # Remove the main PDF file if no longer needed
    file.delete_file(local_path)

    return images


class Vision:
    def __init__(self, account_id: int, files: List[MediaSource]):
        self.files = files
        self.account_id = account_id
        self.ai_client = ai.AIService(AI_PROVIDER, self.account_id)

    async def get_content(self) -> Tuple[str, UsageData]:
        urls = []
        for f in self.files:
            url = f.url
            if f.is_private:
                url = s3.generate_presigned_url(f.url)
            urls.append(url)

        return await self.ai_client.ocr(urls)


class Whisper:
    def __init__(self, account_id: int, files: List[MediaSource]):
        self.files = files
        self.account_id = account_id
        self.ai_client = ai.AIService("openai", self.account_id)

    async def get_content(self) -> Tuple[str, UsageData]:
        urls = []
        for f in self.files:
            url = f.url
            if f.is_private:
                url = s3.generate_presigned_url(f.url)
            urls.append(url)

        return await self.ai_client.speech_to_text(urls)


class Reader:
    def __init__(self, file_path: str, account_id: int):
        self.file_path = file_path
        self.account_id = account_id

    async def get_content_async(self) -> Optional[str]:
        loop = asyncio.get_running_loop()

        # Обработка PDF асинхронно через executor
        content: str = await loop.run_in_executor(None, self.extract_text)

        if content:
            return content.strip()
        return None

    def extract_text(self) -> str:
        content = ""

        if self.file_path.endswith('.pdf'):  # Check if it's a text file
            doc = fitz.open(self.file_path)  # Using fitz to open the file
            for page in doc:
                text = page.get_text()
                content += "\n\n" + text
            doc.close()
        else:  # For other supported formats like PDF, XPS, etc.
            with open(self.file_path, 'r') as f:
                return f.read()
        return content


class Splitter:
    min_size = 8000
    max_size = 9000

    def __init__(self) -> None:
        pass

    def split(self, content: str) -> List[str]:
        """Читает PDF документ, извлекает из него текст и складывает в блоки.
        Размер блока находится между min_block_size и max_block_size символов.
        Гарантируется, что блок не закончится посередине параграфа.

        :param content: текст для разделения
        :return: список блоков текста.
        """
        blocks = []
        current_block = ""

        LINE_END_CHARS = ('.', '?', '!', ':', ';', '—', '”', '…')

        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Удаление случайных переносов строки в середине предложения
            if not line.endswith(LINE_END_CHARS):
                # Если строка не заканчивается знаком препинания, соединяем ее со следующей
                current_block += line + ' '  # Добавляем пробел, предполагая перенос слова
            else:
                # Если строка заканчивается знаком препинания, обрабатываем как конец предложения/абзаца
                current_block += line + '\n'

            # Проверка размера текущего блока
            if len(current_block) >= self.min_size:
                if len(current_block) <= self.max_size or line.endswith(LINE_END_CHARS):
                    # Если текущий блок в пределах максимального размера или строка заканчивается на знак препинания
                    blocks.append(current_block)
                    current_block = ""
                else:
                    # Если следующая строка может быть началом нового абзаца
                    if i + 1 < len(lines) and lines[i + 1].strip() != '':
                        blocks.append(current_block.strip())
                        current_block = ""

        # Добавляем последний блок, если он не пустой
        if current_block.strip() != "":
            blocks.append(current_block)

        return blocks
