from io import BytesIO
from PIL import Image
from fastapi import UploadFile
import pytesseract


async def extract_markup(file: UploadFile) -> str:
    try:
        match file.content_type:
            case (
                "text/xml"
                | "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                return (await file.read()).decode("utf-8")
            case (
                "image/bmp"
                | "image/jpeg"
                | "image/png"
                | "image/jpeg"
                | "application/pdf"
            ):
                image = Image.open(BytesIO(await file.read()))
                e = pytesseract.image_to_alto_xml(image)
                return e
            case _:
                raise f"File type {file.content_type} isn't supported"
        # extracted_text = pytesseract.image_to_string(image)
        # return extracted_text
    except Exception as ex:
        raise ex
