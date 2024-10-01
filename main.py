import os
from io import BytesIO
from dotenv import load_dotenv
from typing import Any
from fastapi import Body, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse, StreamingResponse
from src.entities.file_entity import FileEntity
from src.entities.s3_file_entity import S3FileEntity
from src.entities.json_schema_entity import JsonSchemaEntity
from src.entities.schema_entity import SchemaEntity
from src.dtos.json_schema_dto import JsonSchemaDto
from src.dtos.schema_dto import SchemaDto
from src.S3 import S3Client, S3Config
from src.ocr import extract_markup
from src.mongodb import load_collection, MongoConfig, SchemaCollection, FileCollection
from src.pipelines import rag_pipeline


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute before application starts
    await load_collection(
        MongoConfig(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"))
    )
    yield
    # Execute after the application has finished


app = FastAPI(
    title="Docuxtract API",
    summary="A simple way of extracting document data.",
    description="This API is intended to be easy for developers to add value with document extraction tools.",
    lifespan=lifespan,
)


file_collection = FileCollection()
schema_collection = SchemaCollection()

s3_client = S3Client(
    S3Config(
        url=os.getenv("S3_URL"),
        access_key=os.getenv("S3_ACESS_KEY"),
        secret_access_key=os.getenv("S3_SECRET_KEY"),
        bucket=os.getenv("S3_BUCKET"),
        region=os.getenv("S3_REGION"),
    )
)


@app.post("/bucket")
def create_bucket() -> None:
    s3_client.create_butcket()


@app.post("/upload")
async def upload_file(file: UploadFile) -> None:
    try:
        _, ext = os.path.splitext(file.filename)
        content = await file.read()
        s3_file = S3FileEntity(ext=ext, content=content)

        if not await file_collection.has(s3_file.key):
            s3_client.upload_file(s3_file)
            await file_collection.insert(
                FileEntity(name=file.filename, key=s3_file.key)
            )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/download")
async def download_file(key: str) -> StreamingResponse:
    try:
        file = await file_collection.find_by_key(key)
        s3_file = s3_client.download_file(file.key)
        return StreamingResponse(
            BytesIO(s3_file.content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file.name}"},
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post(
    "/schema/validate",
    responses={
        "200": {
            "description": "`true` if the schema is valid or `false` If the schema is not valid.",
            "content": {"application/json": {"example": "true"}},
        }
    },
)
def validate_schema(
    schema: JsonSchemaDto = Body(..., description="The schema to be validated.")
) -> bool:
    """
    Check if the provided schema is valid.
    """
    try:
        entity = JsonSchemaEntity(**schema.model_dump())
        return entity.is_valid
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid schema\n{str(ex)}")


@app.put("/schema", status_code=204)
async def create_schema(
    schema: SchemaDto = Body(..., description="The schema to be created or updated.")
) -> None:
    """
    Create a new schema or update an existing one if the `id` property is provided.
    """
    try:
        if schema.id != None:
            return JSONResponse(
                status_code=500,
                content={"message": "Unsuported update operation"},
            )

        json_schema_entity = JsonSchemaEntity(**schema.json_schema.model_dump())
        if not json_schema_entity.json_schema.is_valid:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid schema"},
            )

        await schema_collection.insert(
            SchemaEntity(id=schema.id, name=schema.name, json_schema=json_schema_entity)
        )
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )


@app.post(
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
async def ocr(
    file: UploadFile = File(..., description="File to process through OCR.")
) -> str:
    """
    Run only the OCR tool and return OCR processing.
    """
    return await extract_markup(file)


@app.post(
    "/process",
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
async def process(
    n: str = Query(
        ..., description="The name of the output schema to be used in the pipeline."
    ),
    q: str = Query(..., description="The query to be made to the pipeline."),
    file: UploadFile = File(
        ..., description="File to be processed through the pipeline."
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
