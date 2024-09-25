from PIL import Image
import pytesseract
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.llms.mistralai import MistralAI
import xml.etree.ElementTree as ET

from instructor import Instructor  # Supondo que haja um módulo chamado 'Instructor'
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# Configuração do Tesseract para OCR
# pytesseract.pytesseract.tesseract_cmd = (
# r"/usr/bin/tesseract"  # Caminho para o Tesseract
# )


# Função para extração de texto usando OCR
def extract_text_via_ocr(image_path):
    # Abrir imagem
    image = Image.open(image_path)

    # Extração de texto
    extracted_text = pytesseract.image_to_string(image)
    print(f"Texto extraído: {extracted_text}")

    return extracted_text


# Função para interpretar o texto extraído usando um modelo LLM (exemplo com LlamaIndex)
def interpret_text_with_llm(path, query_text):
    # Inicializar leitor de dados e o índice do LLM (LlamaIndex, por exemplo)
    # document = Document(text=text)
    documents = SimpleDirectoryReader(input_files=[path]).load_data()
    index = VectorStoreIndex.from_documents(documents=documents)

    # Prevendo com LLM
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)

    print(f"Interpretação do LLM: {response}")

    return response


class InvoiceItem(BaseModel):
    name: str
    qty: int
    rate: int


class Invoice(BaseModel):
    due_date: str
    bill_to_name: str
    items: List[InvoiceItem] = Field(..., description="A list of invoice items")


# Função para estruturar dados interpretados usando o Instructor
def structure_interpreted_data(extracted_text, query_text):
    # Exemplo de estruturação usando 'Instructor' (ajuste de acordo com a documentação real)
    client = instructor.from_openai(
        OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="llama2:7b",  # required, but unused
        ),
        mode=instructor.Mode.JSON,
    )

    structured_data = client.chat.completions.create(
        model="llama2:7b",
        messages=[
            {"role": "system", "content": extracted_text},
            {
                "role": "user",
                "content": query_text,
            },
        ],
        response_model=Invoice,
    )

    print(f"Dados Estruturados: {structured_data.model_dump_json(indent=2)}")

    return structured_data


# Pipeline de extração, interpretação e estruturação
def process_document_pipeline(image_path, query_text):
    # 1. Extração de texto via OCR
    # extracted_text = extract_text_via_ocr(image_path)
    extracted_text = ET.tostring(ET.parse(image_path).getroot(), encoding="unicode")

    # 2. Interpretação dos dados extraídos via LLM
    interpreted_text = interpret_text_with_llm(image_path, query_text)

    # 3. Estruturação das informações extraídas
    structured_data = structure_interpreted_data(extracted_text, query_text)

    return structured_data


# Testar a pipeline com uma imagem de documento
if __name__ == "__main__":
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
    Settings.llm = Ollama(model="llama2:7b", request_timeout=360.0)

    image_path = "invoice.xml"
    resultado = process_document_pipeline(
        image_path, "Get the Due date, Bill to name and items from the invoice"
    )
    print(f"Resultado Final da Pipeline: {resultado}")
