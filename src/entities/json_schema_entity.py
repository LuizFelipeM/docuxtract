from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, create_model
from pydantic_core import PydanticUndefined


class JsonSchemaEntity(BaseModel):
    """
    The schema definition for JSON output validation using Pydantic dynamic model class generation.
    """

    name: str
    """
    Define the field name. Will be used as JSON key when the output JSON is generated.
    """

    type: Literal["datetime", "string", "number", "bool", "object", "array"]
    """
    Define the field type.
    """

    required: bool
    """
    Define if the field is required making the field thrown an error if the field is required and not filled.
    """

    description: str
    """
    Define the field description to be used through the LLM.
    """

    properties: Optional[list[JsonSchemaEntity]] = Field(None)
    """
    Properties are used to define the properties within an `object` type JsonSchema.

    **SHOULD NOT** be used in other JsonSchema's types besides `object` type.
    """

    items: Optional[JsonSchemaEntity] = Field(None)
    """
    Items are used to define the type of items within an `array` type JsonSchema.

    **SHOULD NOT** be used in other JsonSchema's types besides `array` type.
    """

    @property
    def is_valid(self) -> bool:
        """
        Example of valid schema:
        ```
        {
            "name": "invoice",
            "type": "object",
            "required": true,
            "description": "Invoice document data",
            "properties": [
                {
                    "name": "due_date",
                    "type": "datetime",
                    "required": true,
                    "description": "Due date of the invoice"
                },
                {
                    "name": "bill_to_name",
                    "type": "string",
                    "required": false,
                    "description": "Name of the billed company"
                },
                {
                    "name": "items",
                    "type": "array",
                    "required": true,
                    "description": "Items that compose the invoice",
                    "items": {
                        "name": "invoice_items",
                        "type": "object",
                        "required": true,
                        "description": "Items that compose the invoice",
                        "properties": [
                            {
                                "name": "id",
                                "type": "number",
                                "required": true,
                                "description": "Id of the current item"
                            },
                            {
                                "name": "description",
                                "type": "string",
                                "required": true,
                                "description": "Current item description"
                            },
                            {
                                "name": "quantity",
                                "type": "number",
                                "required": true,
                                "description": "Quantity of the current item"
                            },
                            {
                                "name": "rate",
                                "type": "number",
                                "required": true,
                                "description": "Rate of the current item"
                            }
                        ]
                    }
                }
            ]
        }
        ```
        """
        if self.type == "object":
            return self.properties != None and all(
                [prop.is_valid for prop in self.properties]
            )

        if self.type == "array":
            return self.items != None and self.items.is_valid

        return self.properties == None and self.items == None

    # region Pydantic model class generator

    def as_model(self) -> type[BaseModel]:
        """
        Convert the JsonSchema into a Pydantic dynamic model class for field validation.
        """
        attrs = self.attributes_to_model_fields()
        return create_model(self.name, **attrs)

    def attributes_to_model_fields(self) -> Any:
        model_fields: dict[str, tuple[type, Any]] = {}

        if self.type == "object":
            for prop in self.properties:
                model_fields[prop.name] = prop.create_model_tuple()
        else:
            model_fields[self.name] = self.create_model_tuple()

        return model_fields

    def create_model_tuple(self) -> tuple[type, Any]:
        t = self.get_model_type()
        return (
            t if self.required else Optional[t],
            Field(
                ...,
                description=self.description,
            ),
        )

    def get_model_type(self) -> type:
        match self.type:
            case "datetime" | "string":
                return str
            case "number":
                return float
            case "bool":
                return bool
            case "array":
                return list[self.items.get_model_type()]
            case "object":
                return self.as_model()
            case _:
                raise f"Type {self.type} conversion not found"

    # endregion

    # region Schema to LLM prompt generator

    def as_prompt_metadata(self) -> str:
        metadata = f"{self.name}: {self.description}\n"

        if self.type == "object":
            for prop in self.properties:
                metadata += prop.as_prompt_metadata()

        if self.type == "array":
            metadata += self.items.as_prompt_metadata()

        return metadata

    # endregion
