import hashlib
import os
import boto3
from pydantic import BaseModel


class S3Config(BaseModel):
    url: str
    access_key: str
    secret_access_key: str
    region: str
    bucket: str


class S3File(BaseModel):
    ext: str
    content: bytes
    folder_path: str | None = None

    @property
    def key(self) -> str:
        path = ""
        if self.folder_path:
            path = f"{self.folder_path}{"" if self.folder_path.endswith("/") else "/"}"
        return f"{path}{self._hash()}{self.ext}"

    def _hash(self) -> str:
        """Generate SHA-256 hash of the file content."""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(self.content)
        return sha256_hash.hexdigest()


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

    def upload_file(self, file: S3File) -> str:
        self._client.put_object(Bucket=self._bucket, Key=file.key, Body=file.content)
        return file.key

    def download_file(self, key: str) -> S3File:
        _, output_ext = os.path.splitext(key)
        s3_object = self._client.get_object(Bucket=self._bucket, Key=key)
        return S3File(ext=output_ext, content=s3_object["Body"].read())

    def delete_file(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
