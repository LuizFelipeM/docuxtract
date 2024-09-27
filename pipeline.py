import xml.etree.ElementTree as ET
import json
from llm import interpret_text
from src.cls_generator import create_cls


# class InvoiceItem(BaseModel):
#     id: int
#     description: str
#     quantity: int
#     rate: float


# class Invoice(BaseModel):
#     due_date: str = Field()
#     bill_to_name: str = Field()
#     items: list[InvoiceItem] = Field(
#         description="Invoice items described in the invoice file."
#     )


# Pipeline de extração, interpretação e estruturação
def process_document_pipeline(image_path, query_text, output_cls) -> str:
    # 1. Extração de texto via OCR
    # extracted_text = extract_ocr_markup(image_path)
    extracted_text = ET.tostring(ET.parse(image_path).getroot(), encoding="unicode")

    schema = output_cls.model_json_schema()
    # schema = remove_key_in_all_objects("title", schema)

    interpreted_text = interpret_text(
        extracted_text,
        query_text,
        "llama3.1:8b",
        output_cls,
    )

    interpreted_text = interpret_text(
        extracted_text,
        query_text,
        "mistral:7b",
        output_cls,
        json.dumps(schema, indent=2),
    )

    return interpreted_text.model_dump_json(indent=2)


# Testar a pipeline com uma imagem de documento
if __name__ == "__main__":
    schema = {
        "due_date": "datetime",
        "bill_to_name": "str",
        "invoice_items": [
            {"id": "int", "description": "str", "quantity": "int", "rate": "float"}
        ],
    }

    invoice = create_cls("invoice", schema)

    image_path = "invoice.xml"
    resultado = process_document_pipeline(
        image_path, "Get the Due date, Bill to name and invoice items", invoice
    )
    print(f"Resultado Final da Pipeline: {resultado}")
