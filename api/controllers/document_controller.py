import asyncio
import logging
import os
import time
from typing import Tuple

from pdf2image import convert_from_path

from models.document import Document
from models.document import StatusEnum as DocumentStatus
from models.usage_logs import UsageLog
from services import s3
from services.ai_clients.interfaces import UsageData
from services.db.pg_database import SessionLocal
from services.file import delete_file, save_image
from services.kafka import producer
from services.reader import MediaSource, Reader, Splitter, Vision


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


async def read(payload):
    account_id = None
    print('payload', payload)
    logging.info('payload: %s', payload)
    # Получаем документ, ставим статус reading
    with SessionLocal() as db_session:
        document = db_session.get(Document, payload["id"])
        if not document:
            return
        document.status = DocumentStatus.READING
        db_session.commit()
        account_id = document.account_id

    # Скачиваем PDF из S3 асинхронно
    local_path = await s3.download_async(payload['url'])
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")
    # Создаем экземпляр Reader для PDF (предполагаем, что есть асинхронная версия)
    pdf = Reader(local_path, account_id)
    content = await pdf.get_content_async()
    if not content:
        content, usage = await read_ocr(local_path, account_id)
        with SessionLocal() as db_session:
            UsageLog.log(
                db_session,
                {
                    "account_id": account_id,
                    "source_key": "document",
                    "source_id": payload["id"],
                    "operation": "ocr",
                    "input": usage.input_tokens,
                    "output": usage.output_tokens,
                    "embedding": 0,
                },
                usage.model_name,
            )
    delete_file(local_path)
    if not content:
        raise Exception("NO CONTENT IN FILE")

    splitter = Splitter()
    blocks = splitter.split(content)

    # Сохраняем txt контент
    with SessionLocal() as db:
        document = db.get(Document, payload["id"])
        if not document:
            return
        document.set_content(db, content)
        document.create_paragraphs(db, blocks)
        if not document.meta:
            # Отправляем сообщение через асинхронный producer
            producer.send_message(
                'consumer',
                'fill_document_meta',
                f'document_{payload["id"]}',
                {'id': payload["id"]},
            )


async def read_ocr(local_path: str, account_id: int) -> Tuple[str, UsageData]:
    pages = await asyncio.to_thread(convert_from_path, local_path, fmt='png', size=2000)

    images = []
    directory_path = f'storage/{time.time()}'
    remote_path = f'temp/{time.time()}'
    for i, page in enumerate(pages):
        file_name = f'page-{i}.png'
        page_path = f'{directory_path}/{file_name}'

        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # Use a standard synchronous file operation inside a thread for compatibility with PIL
        await asyncio.to_thread(save_image, page, page_path)

        async with s3.get_async_client() as client:
            await s3.upload_async(
                client=client,
                local_path=page_path,
                remote_path=f'{remote_path}/{file_name}',
            )
            images.append(
                MediaSource(
                    url=f'{remote_path}/{file_name}',
                    name=file_name,
                    extension='png',
                    is_private=True,
                )
            )

    vision = Vision(account_id, images)
    return await vision.get_content()
