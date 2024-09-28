from fastapi import UploadFile
from pydantic import BaseModel
from src.llm import interpret_text
from src.ocr import extract_markup


async def rag_pipeline(
    file: UploadFile, query_text: str, output_cls: type[BaseModel]
) -> BaseModel:
    extracted_text = await extract_markup(file)

    # interpreted_text = interpret_text(
    #     extracted_text, query_text, "llama3.1:8b", output_cls, prompt_json_schema=True
    # )

    interpreted_text = interpret_text(
        extracted_text, query_text, "mistral:7b", output_cls, prompt_json_schema=True
    )

    return interpreted_text
