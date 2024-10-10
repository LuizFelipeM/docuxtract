from __future__ import annotations
from beanie import Document, Indexed
from .json_schema_entity import JsonSchemaEntity


class SchemaEntity(Document):
    user: Indexed(str)  # type: ignore
    name: Indexed(str)  # type: ignore
    json_schema: JsonSchemaEntity
