from enum import Enum
from pydantic import BaseModel

from ..enums.ocr_file_type import OCRFileType


class OCRFileDto(BaseModel):
    content: bytes
    type: OCRFileType
