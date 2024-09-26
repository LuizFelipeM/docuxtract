from time import time
from PIL import Image
import pytesseract
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET
from typing import List


class InvoiceItem(BaseModel):
    id: int
    description: str
    quantity: int
    rate: float


class Invoice(BaseModel):
    due_date: str = Field()
    bill_to_name: str = Field()
    items: List[InvoiceItem] = Field(
        description="Invoice items described in the invoice file."
    )


# Função para extração de texto usando OCR
def extract_text_via_ocr(image_path):
    # Abrir imagem
    image = Image.open(image_path)

    # Extração de texto
    extracted_text = pytesseract.image_to_string(image)
    print(f"Texto extraído: {extracted_text}")

    return extracted_text


# Função para interpretar o texto extraído usando um modelo LLM (exemplo com LlamaIndex)
def interpret_text_with_llm(
    extracted_text: str, query_text: str, model: str
) -> BaseModel:
    start_time = time()

    Settings.llm = Ollama(model=model, request_timeout=360.0, json_mode=True)

    prog = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=Invoice),
        prompt_template_str="""
        You are responsible for extracting the required query from an XML file and output the results as a JSON\
        XML: {xml}\
        query: {query}
        """,
        verbose=True,
    )
    result = prog(xml=extracted_text, query=query_text)

    end_time = time()
    print(f"Elapsed time of {model} = {end_time - start_time} seconds")

    return result


# Pipeline de extração, interpretação e estruturação
def process_document_pipeline(image_path, query_text) -> str:
    # 1. Extração de texto via OCR
    # extracted_text = extract_text_via_ocr(image_path)
    extracted_text = ET.tostring(ET.parse(image_path).getroot(), encoding="unicode")

    interpreted_text: BaseModel = interpret_text_with_llm(
        extracted_text, query_text, "llama3.1:8b"
    )

    interpreted_text: BaseModel = interpret_text_with_llm(
        extracted_text, query_text, "qwen2.5:7b"
    )

    return interpreted_text.model_dump_json(indent=2)


# Testar a pipeline com uma imagem de documento
if __name__ == "__main__":
    image_path = "invoice.xml"
    resultado = process_document_pipeline(
        image_path, "Get the Due date, Bill to name and invoice items"
    )
    print(f"Resultado Final da Pipeline: {resultado}")
