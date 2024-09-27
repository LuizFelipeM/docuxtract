from typing import Any, Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/")
def validate_schema(schema: dict[str, Any] | list[Any]):
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
    return schema_validator(schema)


def schema_validator(schema: dict[str, Any] | list[Any]) -> bool:
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
            if not schema_validator(value):
                return False
        return True

    if isinstance(schema, list):
        if len(schema) == 1:
            return schema_validator(schema[0])

    if isinstance(schema, str):
        return schema in ["datetime", "str", "int", "float", "bool"]

    return False
