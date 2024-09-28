from typing import Any, Union
from src.mongodb.schema_collection import JsonSchema, SchemaField


def remove_key_recursive(key: str, schema: dict[str, Any]) -> dict[str, Any]:
    if isinstance(schema, dict):
        schema.pop(key, None)
        for _, value in schema.items():
            remove_key_recursive(key, value)
    elif isinstance(schema, list):
        for item in schema:
            remove_key_recursive(key, item)
    return schema


def is_valid_schema(schema: Union[SchemaField, JsonSchema]) -> bool:
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
    if isinstance(schema, dict):
        for _, value in schema.items():
            if not is_valid_schema(value):
                return False
        return True

    if isinstance(schema, list):
        if len(schema) == 1:
            return is_valid_schema(schema[0])

    return isinstance(schema, SchemaField)
