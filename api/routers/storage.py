import uuid

from fastapi import APIRouter, Body, File, UploadFile

from config import s3
from services.s3 import generate_presigned_url, s3_client
from validators.storage_requests import DownloadRequest

router = APIRouter(prefix="/storage")


@router.post("/upload", status_code=200, tags=["storage"])
async def upload_file(file: UploadFile = File(...)):
    unique_id = uuid.uuid4()

    original_filename = file.filename or "default_file_name"

    filename = original_filename.replace(" ", "-")
    file_extension = filename.split('.')[-1].lower()  # Извлекаем расширение файла
    file_type = "other"  # По умолчанию тип файла - другой
    if file_extension in ["pdf"]:
        file_type = "pdf"
    elif file_extension in ["jpg", "jpeg", "png", "gif"]:
        file_type = "image"

    file_path = f"uploads/{unique_id}-{filename}"

    # Начало мультипарт загрузки
    multipart_upload = s3_client.create_multipart_upload(Bucket=s3.S3_BUCKET, Key=file_path)
    upload_id = multipart_upload["UploadId"]

    parts = []
    part_number = 1
    total_size = 0  # Для хранения общего размера файла
    while chunk := await file.read(5 * 1024 * 1024):  # 5MB чанки
        total_size += len(chunk)  # Суммируем размер каждого чанка

        # Загрузка части файла
        part = s3_client.upload_part(
            Bucket=s3.S3_BUCKET,
            Key=file_path,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=chunk,
        )
        parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
        part_number += 1

    # Завершение мультипарт загрузки
    s3_client.complete_multipart_upload(
        Bucket=s3.S3_BUCKET,
        Key=file_path,
        UploadId=upload_id,
        MultipartUpload={"Parts": parts},
    )

    return {
        "filename": filename,
        "file_path": file_path,
        "size": total_size,
        "extension": file_extension,
        "file_type": file_type,
    }


@router.post("/download", status_code=200, tags=["storage"])
def download(request: DownloadRequest = Body(...)):
    # Настройки для доступа к S3
    url = generate_presigned_url(request.path)
    return {"url": url}
