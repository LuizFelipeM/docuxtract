from io import BytesIO
from PIL import Image
from fastapi import UploadFile
import pytesseract


async def extract_markup(file: UploadFile) -> str:
    try:
        if file.content_type.startswith("text/"):
            return (await file.read()).decode("utf-8")

        if file.content_type.startswith("image/"):
            image = Image.open(BytesIO(await file.read()))
            e = pytesseract.image_to_alto_xml(image)
            return e

        raise f"File type {file.content_type} isn't supported"
    except Exception as ex:
        raise ex
