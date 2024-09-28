from dotenv import load_dotenv
from typing import Any, Optional, Union
from fastapi import FastAPI, UploadFile, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.mongodb.schema_collection import SchemaModel
from src.mongodb import SchemaCollection, load_collection
from src.cls_generator import create_cls
from src.pipelines import rag_pipeline
from src.utils import is_valid_schema


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
    json_schema: Union[dict[str, Any], list[Any]]


@app.post("/schema/validate")
def validate_schema(schema: Union[dict[str, Any], list[Any]]):
    """
    Example of valid schema:
    ```
    {
        "due_date": {
            "type": "str",
            "required": true
        },
        "bill_to_name": {
            "type": "str",
            "required": true
        },
        "items": [
            {
                "id": {
                    "type": "int",
                    "required": true
                },
                "description": {
                    "type": "str",
                    "required": true
                },
                "quantity": {
                    "type": "int",
                    "required": true
                },
                "rate": {
                    "type": "float",
                    "required": true
                }
            }
        ]
    }
    ```
    """
    return is_valid_schema(schema)


@app.put("/schema", status_code=status.HTTP_204_NO_CONTENT)
async def create_schema(dto: SchemaDto):
    try:
        if not is_valid_schema(dto.json_schema):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid schema"},
            )

        if dto.id != None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Unsuported update operation"},
            )

        await schema_collection.insert(SchemaModel(**dto.model_dump()))
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
        output_cls = create_cls(n, model.json_schema)
        result = await rag_pipeline(file, q, output_cls)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.model_dump())
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )
