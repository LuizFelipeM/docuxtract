from typing import Any


def remove_key_recursive(key: str, schema: dict[str, Any]) -> dict[str, Any]:
    if isinstance(schema, dict):
        schema.pop(key, None)
        for _, value in schema.items():
            remove_key_recursive(key, value)
    elif isinstance(schema, list):
        for item in schema:
            remove_key_recursive(key, item)
    return schema
