from typing import Any, Dict, Union
import uuid
from fastapi import Body, FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.cls_generator import create_cls
from src.pipelines import rag_pipeline
from src.utils import is_valid_schema


app = FastAPI()


schemas = {}


@app.post("/schema/validate")
def validate_schema(schema: Union[dict[str, Any], list[Any]]):
    """
    Example of valid schema:
    ```
    {
        "due_date": "str",
        "bill_to_name": "str",
        "items": [
            {
                "id": "int",
                "description": "str",
                "quantity": "int",
                "rate": "float"
            }
        ]
    }
    ```
    """
    return is_valid_schema(schema)


class SchemaDto(BaseModel):
    name: str
    json_schema: Union[dict[str, Any], list[Any]]


@app.post("/schema", status_code=status.HTTP_204_NO_CONTENT)
def create_schema(dto: SchemaDto):
    try:
        if not is_valid_schema(dto.json_schema):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid schema"},
            )

        schemas[dto.name] = dto.json_schema
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )


@app.post("/process")
async def process(
    file: UploadFile,
    n: str,
    q: Union[str, None] = None,
) -> str:
    try:
        if n not in schemas:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Schema {n} not found or not created"},
            )
        if q == None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Cannot query with empty query string"},
            )

        output_cls = create_cls(n, schemas[n])
        result = await rag_pipeline(file, q, output_cls)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.model_dump())
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(ex)},
        )
