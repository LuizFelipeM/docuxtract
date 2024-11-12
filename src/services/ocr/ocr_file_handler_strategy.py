from abc import ABC, abstractmethod

from ...dtos.ocr_file_dto import OCRFileDto


class OCRFileHandlerStrategy(ABC):
    @abstractmethod
    def execute(self, file: OCRFileDto) -> bytes:
        pass
