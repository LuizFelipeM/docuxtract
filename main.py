from dotenv import load_dotenv
from typing import Annotated, Any, Optional, Union
from fastapi import Body, FastAPI, UploadFile, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.mongodb.schema_collection import JsonSchema, SchemaModel
from src.mongodb import SchemaCollection, load_collection
from src.cls_generator import create_cls
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
    summary="A simple way of extracting document data",
    description="This API is intended to be easy for developers to extract value from document and add value using it",
    lifespan=lifespan,
)


schema_collection = SchemaCollection()


class SchemaDto(BaseModel):
    id: Optional[str] = None
    name: str
    json_schema: JsonSchema


@app.post("/schema/validate")
def validate_schema(schema: JsonSchema):
    return schema.is_valid


@app.put("/schema", status_code=status.HTTP_204_NO_CONTENT)
async def create_schema(dto: SchemaDto):
    try:
        if not dto.json_schema.is_valid:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid schema"},
            )

        if dto.id != None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Unsuported update operation"},
            )

        await schema_collection.insert(
            SchemaModel(id=dto.id, name=dto.name, json_schema=dto.json_schema)
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )


@app.post("/process")
async def process(
    n: str,
    q: str,
    file: UploadFile,
) -> str:
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
