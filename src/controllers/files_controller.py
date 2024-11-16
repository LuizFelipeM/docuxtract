import logging
from io import BytesIO
import os
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from src import files_service
from src.logger import logger

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{key}")
async def download_file(key: str) -> StreamingResponse:
    try:
        # file = await files_collection.find_by_key(key)
        # s3_file = S3Client.download_file(file.key)
        filename, content = await files_service.download_file(key)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("", status_code=204)
async def upload_file(file: UploadFile) -> None:
    try:
        # _, ext = os.path.splitext(file.filename)
        # content = await file.read()
        # s3_file = S3FileEntity(ext=ext, content=content)

        # if not await files_collection.has_in(s3_file.key):
        #     S3Client.upload_file(s3_file)
        #     await files_collection.insert(
        #         FileEntity(name=file.filename, key=s3_file.key)
        #     )
        name, ext = os.path.splitext(file.filename)
        await files_service.upload_file(name, ext, await file.read())
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.delete("/{key}", status_code=204)
async def delete_file(key: str) -> StreamingResponse:
    try:
        # file = await files_collection.find_by_key(key)
        # s3_file = S3Client.download_file(file.key)
        await files_service.delete_file(key)
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=500, detail=str(ex))
