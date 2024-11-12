import logging
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

from ....logger import logger
from ....dtos.ocr_file_dto import OCRFileDto
from ..preprocess_image import preprocess_image
from ..extract_text_with_tesseract import extract_text_with_tesseract
from ..ocr_file_handler_strategy import OCRFileHandlerStrategy


class TXTStrategy(OCRFileHandlerStrategy):
    def execute(self, file: OCRFileDto) -> bytes:
        content = file.content.decode("utf-8")

        # Define image size and background color
        width, height = 800, 800
        background_color = "white"
        text_color = "black"
        font_size = 15

        # Create a new blank image with white background
        image = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Load a default font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Set text position and line spacing
        padding = 10
        x, y = padding, padding
        line_spacing = font.getsize("A")[1] + 5

        # Draw the text onto the image line by line
        for line in content.splitlines():
            if y + line_spacing > height:
                break  # Stop if text exceeds image height
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_spacing

        result = None
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            try:
                image.save(temp_img.name, format="PNG")
                temp_img.flush()

                preprocessed_image = preprocess_image(temp_img.name)
                result = extract_text_with_tesseract(preprocessed_image)
            except Exception as ex:
                logger.log(logging.ERROR, str(ex))
            os.remove(temp_img.name)

        return result
