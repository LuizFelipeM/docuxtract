from typing import Any, Union


def remove_key_recursive(key: str, schema: dict[str, Any]) -> dict[str, Any]:
    if isinstance(schema, dict):
        schema.pop(key, None)
        for _, value in schema.items():
            remove_key_recursive(key, value)
    elif isinstance(schema, list):
        for item in schema:
            remove_key_recursive(key, item)
    return schema


def is_valid_schema(schema: Union[dict[str, Any], list[Any]]) -> bool:
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
    if isinstance(schema, dict):
        for _, value in schema.items():
            if not is_valid_schema(value):
                return False
        return True

    if isinstance(schema, list):
        if len(schema) == 1:
            return is_valid_schema(schema[0])

    if isinstance(schema, str):
        return schema in ["datetime", "str", "int", "float", "bool"]

    return False
