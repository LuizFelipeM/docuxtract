from ...dtos.ocr_file_dto import OCRFileDto
from .ocr_file_handler_strategy import OCRFileHandlerStrategy


class OCRFileHandlerContext:
    def __init__(self) -> None:
        pass

    @property
    def strategy(self) -> OCRFileHandlerStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: OCRFileHandlerStrategy) -> None:
        self._strategy = strategy

    def extract_data(self, file: OCRFileDto) -> None:
        return self._strategy.execute(file)
