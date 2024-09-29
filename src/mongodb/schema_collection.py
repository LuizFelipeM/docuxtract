from __future__ import annotations
from typing import Any, Literal, Union
from beanie import Document, Indexed
from pydantic import BaseModel, Field, create_model
from pydantic_core import PydanticUndefined


class JsonSchema(BaseModel):
    """ """

    name: str
    type: Literal["datetime", "string", "int", "float", "bool", "object", "array"]
    required: bool
    properties: dict[str, JsonSchema] | None = Field(None)
    items: JsonSchema | None = Field(None)

    @property
    def is_valid(self) -> bool:
        """
        Example of valid schema:
        ```
        {
            "name": "invoice",
            "type": "object",
            "required": true,
            "properties": {
                "due_date": {
                    "name": "due_date",
                    "type": "string",
                    "required": true
                },
                "bill_to_name": {
                    "name": "bill_to_name",
                    "type": "string",
                    "required": true
                },
                "items": {
                    "name": "items",
                    "type": "array",
                    "required": true,
                    "items": {
                        "name": "invoice_items",
                        "type": "object",
                        "required": true,
                        "properties": {
                            "id": {
                                "name": "id",
                                "type": "int",
                                "required": true
                            },
                            "description": {
                                "name": "description",
                                "type": "string",
                                "required": true
                            },
                            "quantity": {
                                "name": "quantity",
                                "type": "int",
                                "required": true
                            },
                            "rate": {
                                "name": "rate",
                                "type": "float",
                                "required": true
                            }
                        }
                    }
                }
            }
        }
        ```
        """
        if self.type == "object":
            return self.properties != None and all(
                [value.is_valid for _, value in self.properties.items()]
            )

        if self.type == "array":
            return self.items != None and self.items.is_valid

        return self.properties == None and self.items == None

    def as_model(self) -> type[BaseModel]:
        attrs = self.attributes_to_model_fields()
        return create_model(self.name, **attrs)

    def attributes_to_model_fields(self) -> Any:
        model_fields: dict[str, tuple[type, Any]] = {}

        if self.type == "object":
            for _, prop in self.properties.items():
                model_fields[prop.name] = prop.create_model_tuple()
        else:
            model_fields[self.name] = self.create_model_tuple()

        return model_fields

    def create_model_tuple(self) -> tuple[type, Any]:
        return (
            self.get_model_type(),
            Field(
                default=(PydanticUndefined if self.required else None),
            ),
        )

    def get_model_type(self) -> type:
        match self.type:
            case "datetime" | "string":
                return str
            case "int":
                return int
            case "float":
                return float
            case "bool":
                return bool
            case "array":
                return list[self.items.get_model_type()]
            case "object":
                return self.as_model()
            case _:
                raise f"Type {self.type} conversion not found"


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
