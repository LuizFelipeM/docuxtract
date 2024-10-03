from typing import Optional
from uuid import UUID
from beanie import Document, Indexed
from pydantic import Field


class FileEntity(Document):
    key: Indexed(str)  # type: ignore
    filename: str
