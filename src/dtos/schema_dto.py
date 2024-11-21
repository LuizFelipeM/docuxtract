from typing import Optional
from pydantic import BaseModel, Field
from .json_schema_dto import JsonSchemaDto


class SchemaDto(BaseModel):
    id: Optional[str] = Field(None)
    name: str
    language: str
    json_schema: JsonSchemaDto
