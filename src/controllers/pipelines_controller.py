from typing import Any
from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import JSONResponse
from ..infrastructure.mongodb import schema_collection
from ..ocr import extract_markup
from ..pipelines import rag_pipeline


router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.post(
    "/ocr",
    responses={
        "200": {
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
async def ocr_pipeline(
    file: UploadFile = File(..., description="File to process through OCR.")
) -> str:
    """
    Run only the OCR tool and return OCR processing.
    """
    return await extract_markup(file)


@router.post(
    "/rag",
    responses={
        "200": {
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
async def rag_pipeline(
    n: str = Query(
        ..., description="The name of the output schema to be used in the pipeline."
    ),
    q: str = Query(..., description="The query to be made to the pipeline."),
    file: UploadFile = File(
        ..., description="File to be processed through the RAG pipeline."
    ),
) -> dict[str, Any]:
    """
    Process the document with the specific schema through the RAG Pipeline.
    """
    try:
        if not q:
            return JSONResponse(
                status_code=400,
                content={"message": f"Cannot query with empty query string"},
            )

        if not n or not (await schema_collection.has(n)):
            return JSONResponse(
                status_code=400,
                content={"message": f"Schema {n} not found or not created"},
            )

        entity = await schema_collection.find_by_name(n)
        output_cls = entity.json_schema.as_model()
        result = await rag_pipeline(file, q, output_cls)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )
