import os
import boto3
from pydantic import BaseModel
from src.entities.s3_file_entity import S3FileEntity


class S3Config(BaseModel):
    url: str
    access_key: str
    secret_access_key: str
    region: str
    bucket: str


class S3Client:
    _bucket: str

    def __init__(self, config: S3Config) -> None:
        self._bucket = config.bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=config.url,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_access_key,
            region_name=config.region,
        )

    def create_butcket(self) -> None:
        self._client.create_bucket(Bucket=self._bucket)

    def upload_file(self, file: S3FileEntity) -> str:
        self._client.put_object(Bucket=self._bucket, Key=file.key, Body=file.content)
        return file.key

    def download_file(self, key: str) -> S3FileEntity:
        _, output_ext = os.path.splitext(key)
        s3_object = self._client.get_object(Bucket=self._bucket, Key=key)
        return S3FileEntity(ext=output_ext, content=s3_object["Body"].read())

    def delete_file(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
