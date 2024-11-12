import logging
import os
import tempfile
from io import BytesIO

from ....logger import logger
from ....dtos.ocr_file_dto import OCRFileDto, OCRFileType
from ..ocr_file_handler_strategy import OCRFileHandlerStrategy
from ..extract_text_with_tesseract import extract_text_with_tesseract
from ..preprocess_image import preprocess_image


class ImageStrategy(OCRFileHandlerStrategy):
    def _to_extension(self, type: OCRFileType) -> str:
        match type:
            case OCRFileType.JPG:
                return ".jpg"
            case OCRFileType.PNG:
                return ".png"
            case OCRFileType.TIFF:
                return ".tiff"
            case OCRFileType.WEBP:
                return ".webp"

        raise ValueError("Unsupported file format")

    def execute(self, file: OCRFileDto) -> bytes:
        ocr_result = None
        with tempfile.NamedTemporaryFile(
            suffix=self._to_extension(file.type), delete=False
        ) as temp_img:
            try:
                temp_img.write(file.content)
                temp_img.flush()

                preprocessed_image = preprocess_image(temp_img.name)
                ocr_result = extract_text_with_tesseract(preprocessed_image)
            except Exception as ex:
                logger.log(logging.ERROR, str(ex))
            os.remove(temp_img.name)
        return ocr_result
