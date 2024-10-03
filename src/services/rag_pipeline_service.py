import json
import os
from uuid import UUID
from fastapi import UploadFile
from pydantic import BaseModel

from ..entities.s3_file_entity import S3FileEntity
from ..infrastructure.S3 import S3Client

from .files_service import FilesService
from .llm import interpret_text
from .ocr import extract_markup


class RAGPipelineService:
    def __init__(self, files_service: FilesService, s3_client: S3Client) -> None:
        self._files_service = files_service
        self._s3_client = s3_client

    async def process(
        self,
        file: UploadFile,
        query_text: str,
        output_cls: type[BaseModel],
        request_id: UUID,
    ) -> BaseModel:
        try:
            file_content = await file.read()
            name, ext = os.path.splitext(file.filename)

            # Upload file to S3 an register
            key = await self._files_service.upload_file(name, ext, file_content)

            # Extract file markup data
            extracted_content = await extract_markup(
                file.content_type, file_content, request_id
            )

            # Log OCR output

            # Process extracted markup data
            extracted_text = extracted_content.decode("utf-8")

            # interpreted_text = interpret_text(
            #     extracted_text, query_text, "llama3.1:8b", output_cls, request_id, prompt_json_schema=True
            # )

            result = interpret_text(
                extracted_text,
                query_text,
                "mistral:7b",
                output_cls,
                request_id,
                prompt_json_schema=True,
            )

            # Log LLM output

            return result
        except Exception as ex:
            raise f"Unable to process the pipeline {request_id}"
