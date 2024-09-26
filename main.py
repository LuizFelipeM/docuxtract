from time import time
from PIL import Image
import pytesseract
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, create_model
import xml.etree.ElementTree as ET
from typing import Any, List, Type
import json


# class InvoiceItem(BaseModel):
#     id: int
#     description: str
#     quantity: int
#     rate: float


# class Invoice(BaseModel):
#     due_date: str = Field()
#     bill_to_name: str = Field()
#     items: List[InvoiceItem] = Field(
#         description="Invoice items described in the invoice file."
#     )


# Função para extração de texto usando OCR
def extract_text_via_ocr(image_path):
    # Abrir imagem
    image = Image.open(image_path)

    # Extração de texto
    extracted_text = pytesseract.image_to_string(image)
    print(f"Texto extraído: {extracted_text}")

    return extracted_text


def remove_key_in_all_objects(key: str, schema: dict[str, Any]) -> dict[str, Any]:
    # If the schema is a dictionary, iterate through its keys
    if isinstance(schema, dict):
        schema.pop(key, None)  # Remove the 'title' key if present
        for _, value in schema.items():
            # Recursively remove 'title' in nested dictionaries
            remove_key_in_all_objects(key, value)
    # If the schema is a list, iterate through its items
    elif isinstance(schema, list):
        for item in schema:
            remove_key_in_all_objects(key, item)
    return schema


# Função para interpretar o texto extraído usando um modelo LLM (exemplo com LlamaIndex)
def interpret_text_with_llm(
    extracted_text: str, query_text: str, model: str, output_cls: Any, json_schema=""
) -> BaseModel:
    start_time = time()

    Settings.llm = Ollama(
        model=model, temperature=0.2, request_timeout=360.0, json_mode=True
    )

    prog = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=output_cls),
        prompt_template_str="""
        You are responsible for extracting the required query from an XML file and output the results as a JSON {json_schema}\
        XML: {xml}\
        query: {query}
        """,
        verbose=True,
    )

    if json_schema:
        json_schema = f"""
        based on the following JSON schema:\
        {json_schema}
        """

    result = prog(xml=extracted_text, query=query_text, json_schema=json_schema)

    end_time = time()
    print(f"Elapsed time of {model} = {end_time - start_time} seconds")

    return result


# Pipeline de extração, interpretação e estruturação
def process_document_pipeline(image_path, query_text, output_cls) -> str:
    # 1. Extração de texto via OCR
    # extracted_text = extract_text_via_ocr(image_path)
    extracted_text = ET.tostring(ET.parse(image_path).getroot(), encoding="unicode")

    schema = output_cls.model_json_schema()
    # schema = remove_key_in_all_objects("title", schema)

    interpreted_text: BaseModel = interpret_text_with_llm(
        extracted_text,
        query_text,
        "llama3.1:8b",
        output_cls,
    )

    interpreted_text: BaseModel = interpret_text_with_llm(
        extracted_text,
        query_text,
        "mistral:7b",
        output_cls,
        json.dumps(schema, indent=2),
    )

    return interpreted_text.model_dump_json(indent=2)


def generate_model(name: str, attributes: dict[str, Any]) -> Type[BaseModel]:
    attrs = attributes_to_model_fields(attributes)
    model = create_model(name, **attrs)
    return model


def attributes_to_model_fields(schema: dict[str, Any]) -> Any:
    model_fields: dict[str, tuple[type, Any]] = {}

    if isinstance(schema, dict):
        for key, value in schema.items():
            model_fields[key] = generate_model_tuple(key, value)

    if isinstance(schema, list):
        model_fields[key] = generate_model_tuple(key, schema[0])

    return model_fields


def generate_model_tuple(key: str, value: Any) -> tuple[type, Any]:
    return (get_model_type(key, value), ...)


def get_model_type(key: str, value: Any) -> type:
    if isinstance(value, dict):
        return generate_model(key, value)

    if isinstance(value, list):
        return List[get_model_type(key, value[0])]

    match value:
        case "datetime" | "str":
            return str
        case "int":
            return int
        case "float":
            return float
        case _:
            raise f"Type {value} conversion not found"


# Testar a pipeline com uma imagem de documento
if __name__ == "__main__":
    schema = {
        "due_date": "datetime",
        "bill_to_name": "str",
        "invoice_items": [
            {"id": "int", "description": "str", "quantity": "int", "rate": "float"}
        ],
    }

    invoice = generate_model("invoice", schema)
    # print(json.dumps(invoice.model_json_schema(), indent=2))

    image_path = "invoice.xml"
    resultado = process_document_pipeline(
        image_path, "Get the Due date, Bill to name and invoice items", invoice
    )
    print(f"Resultado Final da Pipeline: {resultado}")
