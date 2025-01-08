import os
import uuid
from time import time
from typing import Optional
from urllib.parse import unquote, urlparse

import aiofiles
import aiohttp
import requests


def is_pdf(url: str) -> bool:
    """Определяет, является ли файл по указанному URL PDF-файлом."""
    path = urlparse(unquote(url)).path
    return path.lower().endswith('.pdf')


def is_image(url: str) -> bool:
    """Определяет, является ли файл по указанному URL изображением."""
    formats = [".png", ".jpeg", ".jpg", ".webp"]
    path = urlparse(unquote(url)).path
    return any(path.lower().endswith(f) for f in formats)


def is_audio(url: str) -> bool:
    """Определяет, является ли файл по указанному URL аудиофайлом."""
    formats = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".flac"]
    path = urlparse(unquote(url)).path
    return any(path.lower().endswith(f) for f in formats)


def is_private(url: str) -> bool:
    return not url.lower().startswith("https")


def get_type(url: str) -> str:
    if is_image(url):
        return "image"
    if is_pdf(url):
        return "pdf"
    if is_audio(url):
        return "audio"
    return "other"


def download(url: str, local_path: Optional[str] = None) -> str:
    if local_path is None:
        rand = uuid.uuid4()
        path = urlparse(unquote(url)).path
        local_path = f'storage/{rand}_{path}'

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    response = requests.get(url)
    with open(local_path, 'wb') as file:
        file.write(response.content)

    return local_path


def delete_file(local_path: str) -> None:
    if os.path.exists(local_path):
        os.remove(local_path)


async def download_async(url: str, local_path: Optional[str] = None) -> str:
    if local_path is None:
        path = urlparse(unquote(url)).path
        local_path = f'storage/{time()}_{os.path.basename(path)}'

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(local_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
            else:
                raise Exception(f"Failed to download file: {response.status}")

    return local_path


def save_image(page, path: str) -> None:
    """Сохраняет изображение в указанном пути."""
    with open(path, 'wb') as f:
        page.save(f, 'PNG')
