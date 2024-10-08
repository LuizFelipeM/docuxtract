from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class JsonSchemaDto(BaseModel):
    name: str
    type: Literal["datetime", "string", "number", "bool", "object", "array"]
    required: bool
    description: str
    properties: Optional[list[JsonSchemaDto]] = Field(None)
    items: Optional[JsonSchemaDto] = Field(None)
