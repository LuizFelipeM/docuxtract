import logging
import os
import tempfile
from pdf2image import convert_from_bytes

from ....logger import logger
from ....dtos.ocr_file_dto import OCRFileDto
from ..preprocess_image import preprocess_image
from ..extract_text_with_tesseract import extract_text_with_tesseract
from ..ocr_file_handler_strategy import OCRFileHandlerStrategy


class PDFStrategy(OCRFileHandlerStrategy):
    def execute(self, file: OCRFileDto) -> bytes:
        images = convert_from_bytes(file.content)
        ocr_results = []

        for _, image in enumerate(images):
            # Save image to temp file to read in OpenCV
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
                try:
                    image.save(temp_img.name, format="PNG")
                    preprocessed_image = preprocess_image(temp_img.name)
                    ocr_results.append(extract_text_with_tesseract(preprocessed_image))
                except Exception as ex:
                    logger.log(logging.ERROR, str(ex))
                os.remove(temp_img.name)
        return b"\n".join(ocr_results)
