from enum import Enum


class OCRFileType(Enum):
    """
    Represents the current supported file types
    """

    JPG = 0
    JPEG = 0
    PNG = 1
    TIFF = 3
    WEBP = 4
    DOCX = 5
    PDF = 6
