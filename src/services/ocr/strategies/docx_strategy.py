import logging
import os
import tempfile
from spire.doc import Document, Stream, ImageType

from ....dtos.ocr_file_dto import OCRFileDto
from ....logger import logger
from ..ocr_file_handler_strategy import OCRFileHandlerStrategy
from ..preprocess_image import preprocess_image
from ..extract_text_with_tesseract import extract_text_with_tesseract


class DOCXStrategy(OCRFileHandlerStrategy):
    def execute(self, file: OCRFileDto) -> bytes:
        document = Document(Stream(file.content))

        results = []
        for i in range(document.GetPageCount()):
            page_stream = document.SaveImageToStreams(i, ImageType.Bitmap)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
                try:
                    temp_img.write(page_stream.ToArray())
                    temp_img.flush()

                    preprocessed_image = preprocess_image(temp_img.name)
                    results.append(extract_text_with_tesseract(preprocessed_image))
                except Exception as ex:
                    logger.log(logging.ERROR, str(ex))
                os.remove(temp_img.name)

        return b"\n".join(results)

    # def execute(self, file: OCRFileDto) -> bytes | None:
    #     # Process DOCX files to extract text directly
    #     doc = Document(BytesIO(file.content))
    #     alto_xml_root = docx_to_alto_xml_text(doc)

    #     # Convert embedded images for OCR
    #     ocr_results = []
    #     for rel in doc.part.rels.values():
    #         if "image" in rel.target_ref or "media" in rel.target_ref:
    #             with tempfile.NamedTemporaryFile(
    #                 suffix=f".{rel.target_ref.split(".")[-1]}", delete=False
    #             ) as temp_img:
    #                 try:
    #                     temp_img.write(rel.target_part.blob)
    #                     temp_img.flush()

    #                     preprocessed_image = preprocess_image(temp_img.name)
    #                     ocr_results.append(extract_text_with_tesseract(preprocessed_image))
    #                 except Exception as ex:
    #                     logger.log(logging.ERROR, str(ex))
    #                 os.remove(temp_img.name)

    #     # Combine text and image OCR results
    #     return b"\n".join([ET.tostring(alto_xml_root, encoding="utf-8"), *ocr_results])
