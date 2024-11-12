from ...dtos.ocr_file_dto import OCRFileDto, OCRFileType
from .strategies.image_strategy import ImageStrategy
from .strategies.pdf_strategy import PDFStrategy
from .strategies.docx_strategy import DOCXStrategy
from .ocr_file_handler_context import OCRFileHandlerContext


context = OCRFileHandlerContext()


def extract_markup(content_type: str, content: bytes) -> bytes:
    content_subtype = content_type.split("/")[-1]
    type: OCRFileType = None

    if content_type.startswith("image"):
        type = OCRFileType[content_subtype.upper()]
        context.strategy = ImageStrategy()

    match content_subtype:
        case "pdf":
            type = OCRFileType.PDF
            context.strategy = PDFStrategy()
        case "vnd.openxmlformats-officedocument.wordprocessingml.document":
            type = OCRFileType.DOCX
            context.strategy = DOCXStrategy()

    return context.extract_data(OCRFileDto(content=content, type=type))
