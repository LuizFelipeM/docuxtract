import os
from io import BytesIO
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from ..infrastructure.S3 import S3Client, S3Config
from ..entities.file_entity import FileEntity
from ..entities.s3_file_entity import S3FileEntity
from ..infrastructure.mongodb import FileCollection

file_collection = FileCollection()
s3_client = S3Client(
    S3Config(
        url=os.getenv("S3_URL"),
        access_key=os.getenv("S3_ACESS_KEY"),
        secret_access_key=os.getenv("S3_SECRET_KEY"),
        bucket=os.getenv("S3_BUCKET"),
        region=os.getenv("S3_REGION"),
    )
)

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{key}")
async def download_file(key: str) -> StreamingResponse:
    try:
        file = await file_collection.find_by_key(key)
        s3_file = S3Client.download_file(file.key)
        return StreamingResponse(
            BytesIO(s3_file.content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file.name}"},
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/")
async def upload_file(file: UploadFile) -> None:
    try:
        _, ext = os.path.splitext(file.filename)
        content = await file.read()
        s3_file = S3FileEntity(ext=ext, content=content)

        if not await file_collection.has(s3_file.key):
            S3Client.upload_file(s3_file)
            await file_collection.insert(
                FileEntity(name=file.filename, key=s3_file.key)
            )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.delete("/{key}")
async def delete_file(key: str) -> StreamingResponse:
    try:
        file = await file_collection.find_by_key(key)
        s3_file = S3Client.download_file(file.key)
        return StreamingResponse(
            BytesIO(s3_file.content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file.name}"},
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
