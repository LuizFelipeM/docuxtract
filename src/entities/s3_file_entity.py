import hashlib
from typing import Optional
from pydantic import BaseModel


class S3FileEntity(BaseModel):
    ext: str
    content: bytes

    @property
    def name(self) -> str:
        """Generate SHA-256 hash name of the file content."""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(self.content)
        return sha256_hash.hexdigest()

    @property
    def key(self) -> str:
        return f"{self.name}{self.ext}"
