from PIL import Image
import pytesseract


def extract_ocr_markup(image_path: str):
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text
