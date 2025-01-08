import os
import shutil
import time
from typing import Optional, Tuple

import aioboto3
import boto3
from botocore.client import BaseClient

from config.s3 import S3_ACCESS_KEY, S3_BUCKET, S3_ENDPOINT_URL, S3_SECRET_KEY

# Создание клиента S3
s3_client: BaseClient = boto3.client(
    's3',
    region_name="us-west-1",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)


class StorageService:
    def __init__(self) -> None:
        session = aioboto3.Session()

        self.async_client: BaseClient = session.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            endpoint_url=S3_ENDPOINT_URL,
        )

        self.client: BaseClient = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
        )

    async def read_content_async(self, remote_path: str) -> Tuple[str, str]:
        response = await self.async_client.get_object(Bucket=S3_BUCKET, Key=remote_path)
        object_body = await response['Body'].read()
        content = object_body.decode('utf-8')
        return content, remote_path

    def read_content(self, remote_path: str) -> str:
        response = self.client.get_object(Bucket=S3_BUCKET, Key=remote_path)
        object_body: str = response['Body'].read().decode('utf-8')
        return object_body


def get_async_client() -> BaseClient:
    session = aioboto3.Session()
    return session.client(
        "s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    )


def download(file_name: str, local_path: Optional[str] = None) -> str:
    if local_path is None:
        local_path = f'storage/{time.time()}_{file_name.replace("/", "-")}'
    s3_client.download_file(Bucket=S3_BUCKET, Key=file_name, Filename=local_path)
    return local_path


async def download_async(file_name: str, local_path: Optional[str] = None) -> str:
    if local_path is None:
        local_path = f'storage/{time.time()}_{file_name.replace("/", "-")}'
    async with get_async_client() as client:
        await client.download_file(Bucket=S3_BUCKET, Key=file_name, Filename=local_path)
    return local_path


def upload(local_path: str, remote_path: str) -> None:
    s3_client.upload_file(local_path, S3_BUCKET, remote_path)


async def upload_async(client: BaseClient, local_path: str, remote_path: str) -> None:
    await client.upload_file(local_path, S3_BUCKET, remote_path)


def put_object(remote_path: str, content: str) -> None:
    s3_client.put_object(Bucket=S3_BUCKET, Key=remote_path, Body=content)


def read_content(remote_path: str) -> str:
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=remote_path)
    object_body: str = response['Body'].read().decode('utf-8')
    return object_body


async def read_content_async(client: BaseClient, remote_path: str) -> Tuple[str, str]:
    response = await client.get_object(Bucket=S3_BUCKET, Key=remote_path)
    object_body = await response['Body'].read()
    content = object_body.decode('utf-8')
    return content, remote_path


def generate_presigned_url(path: str) -> str:
    url: str = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': path,
        },
        ExpiresIn=3600,
    )
    return url


def prepare_dir(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
