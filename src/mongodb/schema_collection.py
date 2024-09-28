from typing import Any, Literal, Union
from beanie import Document, Indexed
from pydantic import BaseModel


class SchemaField(BaseModel):
    type: Union[
        Literal["datetime"],
        Literal["str"],
        Literal["int"],
        Literal["float"],
        Literal["bool"],
    ]
    required: bool


JsonSchema = Union[dict[str, Union[SchemaField, Any]], list[Union[SchemaField, Any]]]


class SchemaModel(Document):
    name: Indexed(str)  # type: ignore
    json_schema: JsonSchema


class SchemaCollection:
    async def insert(self, schema: SchemaModel) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> SchemaModel:
        return await SchemaModel.find_one(SchemaModel.id == id)

    async def find_by_name(self, name: str) -> SchemaModel:
        return await SchemaModel.find_one(SchemaModel.name == name)

    async def has(self, name: str) -> bool:
        return await SchemaModel.find_one(SchemaModel.name == name) != None
        # return await self.session.schemas.count_documents({"name": name}) != 0
