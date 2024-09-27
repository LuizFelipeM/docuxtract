from pydantic import BaseModel, create_model
from typing import Any, Type, Union


def create_cls(
    name: str, attributes: Union[dict[str, Any], list[Any]]
) -> Type[BaseModel]:
    attrs = attributes_to_model_fields(attributes)
    model = create_model(name, **attrs)
    return model


def attributes_to_model_fields(schema: Union[dict[str, Any], list[Any]]) -> Any:
    model_fields: dict[str, tuple[type, Any]] = {}

    if isinstance(schema, dict):
        for key, value in schema.items():
            model_fields[key] = create_model_tuple(key, value)

    # Refactor
    # if isinstance(schema, list):
    #     model_fields[key] = create_model_tuple(key, schema[0])

    return model_fields


def create_model_tuple(key: str, value: Any) -> tuple[type, Any]:
    return (get_model_type(key, value), ...)


def get_model_type(key: str, value: Any) -> type:
    if isinstance(value, dict):
        return create_cls(key, value)

    if isinstance(value, list):
        return list[get_model_type(key, value[0])]

    match value:
        case "datetime" | "str":
            return str
        case "int":
            return int
        case "float":
            return float
        case "bool":
            return bool
        case _:
            raise f"Type {value} conversion not found"
