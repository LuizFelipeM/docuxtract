from typing import Optional
from pydantic import BaseModel
from .json_schema_dto import JsonSchemaDto


class SchemaDto(BaseModel):
    id: Optional[str] = None
    name: str
    json_schema: JsonSchemaDto
