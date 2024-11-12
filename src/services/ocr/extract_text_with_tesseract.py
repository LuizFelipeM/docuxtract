import cv2
import pytesseract


def extract_text_with_tesseract(image: cv2.typing.MatLike) -> bytes:
    ocr_data = pytesseract.image_to_alto_xml(image)
    if isinstance(ocr_data, str):
        return ocr_data.encode("utf-8")
    return ocr_data
