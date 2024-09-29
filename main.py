from dotenv import load_dotenv
from typing import Any, Optional
from fastapi import Body, FastAPI, Query, UploadFile, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.ocr import extract_markup
from src.mongodb.schema_collection import JsonSchema, SchemaModel
from src.mongodb import SchemaCollection, load_collection
from src.pipelines import rag_pipeline


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute before application starts
    await load_collection()
    yield
    # Execute after the application has finished


app = FastAPI(
    title="Docuxtract API",
    summary="A simple way of extracting document data.",
    description="This API is intended to be easy for developers to add value with document extraction tools.",
    lifespan=lifespan,
)


schema_collection = SchemaCollection()


class SchemaDto(BaseModel):
    id: Optional[str] = None
    name: str
    json_schema: JsonSchema


@app.post(
    "/schema/validate",
    responses={
        status.HTTP_200_OK: {
            "description": "`true` if the schema is valid or `false` If the schema is not valid.",
            "content": {"application/json": {"example": "true"}},
        }
    },
)
def validate_schema(
    schema: JsonSchema = Body(..., description="The schema to be validated.")
) -> bool:
    """
    Check if the provided schema is valid.
    """
    return schema.is_valid


@app.put("/schema", status_code=status.HTTP_204_NO_CONTENT)
async def create_schema(
    schema: SchemaDto = Body(..., description="The schema to be created or updated.")
) -> None:
    """
    Create a new schema or update an existing one if the `id` property is provided.
    """
    try:
        if not schema.json_schema.is_valid:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid schema"},
            )

        if schema.id != None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Unsuported update operation"},
            )

        await schema_collection.insert(
            SchemaModel(id=schema.id, name=schema.name, json_schema=schema.json_schema)
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )


@app.post(
    "/ocr",
    responses={
        status.HTTP_200_OK: {
            "description": "The extracted file content if the file is processed sucessfully.",
            "content": {
                "application/json": {
                    "example": """
                    \"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<invoice>\n    <invoice_number>9028</invoice_number>\n    <invoice_date>2024-09-23</invoice_date>\n    <due_date>2024-09-27</due_date>\n\n    <bill_to>\n        <company>BTG Pactual</company>\n        <address>St. Lincon 102</address>\n        <city>Wellington</city>\n        <country>Poland</country>\n        <TRN>Avocado</TRN>\n    </bill_to>\n\n    <ship_to>\n        <name>Test Luiz</name>\n        <address>St. Abraham 09</address>\n        <city>Washington</city>\n        <state>DC</state>\n        <country>U.S.A</country>\n        <TRN>Avocado</TRN>\n    </ship_to>\n\n    <items>\n        <item>\n            <id>1</id>\n            <description>Brochure Design</description>\n            <quantity>2</quantity>\n            <rate>100.00</rate>\n            <vat>12</vat>\n            <amount>200.00</amount>\n        </item>\n        <item>\n            <id>2</id>\n            <description>Agenda</description>\n            <quantity>290</quantity>\n            <rate>20.00</rate>\n            <vat>12</vat>\n            <amount>5800.00</amount>\n        </item>\n        <item>\n            <id>3</id>\n            <description>Clip</description>\n            <quantity>200000</quantity>\n            <rate>0.15</rate>\n            <vat>1</vat>\n            <amount>30000.00</amount>\n        </item>\n        <item>\n            <id>4</id>\n            <description>Smartphone</description>\n            <quantity>1</quantity>\n            <rate>2000.00</rate>\n            <vat>24</vat>\n            <amount>2000.00</amount>\n        </item>\n    </items>\n\n    <totals>\n        <sub_total>38000.00</sub_total>\n        <total_vat>1500.00</total_vat>\n        <total>39500.00</total>\n    </totals>\n\n    <notes>\n        <note>It was great doing business with you.</note>\n    </notes>\n\n    <terms>\n        <term>Please make the payment by the due date.</term>\n    </terms>\n</invoice>\n\"
                    """
                }
            },
        }
    },
)
async def ocr(file: UploadFile) -> str:
    """
    Run only the OCR tool and return OCR processing.
    """
    return await extract_markup(file)


@app.post(
    "/process",
    responses={
        status.HTTP_200_OK: {
            "description": "The processed query data extraction on top of the file in the specified schema `n` format.",
            "content": {
                "application/json": {
                    "example": """
                    {
                        "due_date": "2024-09-27",
                        "bill_to_name": "BTG Pactual",
                        "items": [
                            {
                            "id": 1,
                            "description": "Brochure Design",
                            "quantity": 2,
                            "rate": 100
                            },
                            {
                            "id": 2,
                            "description": "Agenda",
                            "quantity": 290,
                            "rate": 20
                            }
                        ]
                    }
                    """
                }
            },
        }
    },
)
async def process(
    file: UploadFile,
    n: str = Query(
        ..., description="The name of the output schema to be used in the pipeline."
    ),
    q: str = Query(..., description="The query to be made to the pipeline."),
) -> dict[str, Any]:
    """
    Process the document with the specific schema through the RAG Pipeline.
    """
    try:
        if not q:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Cannot query with empty query string"},
            )

        if not n or not (await schema_collection.has(n)):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Schema {n} not found or not created"},
            )

        model = await schema_collection.find_by_name(n)
        output_cls = model.json_schema.as_model()
        result = await rag_pipeline(file, q, output_cls)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.model_dump())
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )
