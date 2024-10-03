import logging

from src.logger import logger

from ..infrastructure.S3 import S3Client
from ..entities.file_entity import FileEntity
from ..entities.s3_file_entity import S3FileEntity
from ..infrastructure.mongodb import FilesCollection


class FilesService:
    def __init__(self, s3_client: S3Client, files_collection: FilesCollection) -> None:
        self._s3_client = s3_client
        self._files_collection = files_collection

    async def download_file(self, key: str) -> tuple[str, bytes]:
        try:
            file = await self._files_collection.find_by_key(key)
            s3_file = self._s3_client.download_file(file.key)
            return file.name, s3_file.content
        except Exception as ex:
            logger.log(logging.ERROR, ex)
            raise f"Unable to download file {key}"

    async def upload_file(self, name: str, ext: str, content: bytes) -> str:
        try:
            s3_file = S3FileEntity(ext=ext, content=content)

            if not await self._files_collection.has(s3_file.key):
                self._s3_client.upload_file(s3_file)
                await self._files_collection.insert(
                    FileEntity(key=s3_file.key, filename=f"{name}{ext}")
                )

            return s3_file.key
        except Exception as ex:
            logger.log(logging.ERROR, ex)
            raise f"Unable to save file {name}{ext}"

    async def delete_file(self, key: str) -> bytes:
        try:
            file = await self._files_collection.find_by_key(key)
            self._s3_client.delete_file(file.key)
            await self._files_collection.delete(file)
        except Exception as ex:
            logger.log(logging.ERROR, ex)
            raise f"Unable to delete file {key}"
