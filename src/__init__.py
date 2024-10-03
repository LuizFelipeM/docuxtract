import os
from .services.rag_pipeline_service import RAGPipelineService
from .services.files_service import FilesService
from .infrastructure.S3 import S3Client, S3Config
from .infrastructure.mongodb import FilesCollection, SchemasCollection


s3_client = S3Client(
    S3Config(
        url=os.getenv("S3_URL"),
        access_key=os.getenv("S3_ACESS_KEY"),
        secret_access_key=os.getenv("S3_SECRET_KEY"),
        bucket=os.getenv("S3_BUCKET"),
        region=os.getenv("S3_REGION"),
    )
)

files_collection = FilesCollection()
schemas_collection = SchemasCollection()

files_service = FilesService(s3_client, files_collection)
rag_pipeline_service = RAGPipelineService(files_service, s3_client)
