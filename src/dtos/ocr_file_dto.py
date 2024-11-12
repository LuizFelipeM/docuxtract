from enum import Enum
from pydantic import BaseModel


class OCRFileType(Enum):
    """
    Represents the current supported file types
    """

    JPG = 0
    PNG = 1
    TIFF = 3
    WEBP = 4
    DOCX = 5
    PDF = 6


class OCRFileDto(BaseModel):
    content: bytes
    type: OCRFileType
