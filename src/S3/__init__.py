import os
from typing import Any
import boto3

client = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_URL"),
    aws_access_key_id=os.getenv("S3_ACESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name=os.getenv("S3_REGION"),
)


class S3Client:
    _bucket = os.getenv("S3_BUCKET")

    def create_butcket(self) -> None:
        client.create_bucket(Bucket=self._bucket)

    def upload_file(self, key: str, file: bytes) -> None:
        client.put_object(Bucket=self._bucket, Key=key, Body=file)

    def download_file(self, key: str) -> Any:
        res = client.get_object(Bucket=self._bucket, Key=key)
        return res["Body"]

    def delete_file(self, key: str) -> None:
        client.delete_object(Bucket=self._bucket, Key=key)
