from io import BytesIO
from PIL import Image
import pytesseract


async def extract_markup(content_type: str, content: bytes) -> bytes:
    try:
        if content_type.startswith("text/"):
            return content

        if content_type.startswith("image/"):
            image = Image.open(BytesIO(content))
            return pytesseract.image_to_alto_xml(image)

        raise f"File type {content_type} isn't supported"
    except Exception as ex:
        raise ex
