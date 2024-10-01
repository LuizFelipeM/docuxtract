import hashlib
from typing import Optional
from pydantic import BaseModel


class S3FileEntity(BaseModel):
    ext: str
    content: bytes
    folder_path: Optional[str] = None

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
