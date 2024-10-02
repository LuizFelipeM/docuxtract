from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from ..dtos.json_schema_dto import JsonSchemaDto
from ..dtos.schema_dto import SchemaDto
from ..entities.json_schema_entity import JsonSchemaEntity
from ..entities.schema_entity import SchemaEntity
from ..infrastructure.mongodb import SchemaCollection

schema_collection = SchemaCollection()

router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.post(
    "/validate",
    responses={
        "200": {
            "description": "`true` if the schema is valid or `false` If the schema is not valid.",
            "content": {"application/json": {"example": "true"}},
        }
    },
)
def validate_schema(
    schema: JsonSchemaDto = Body(..., description="The schema to be validated.")
) -> bool:
    """
    Check if the provided schema is valid.
    """
    try:
        entity = JsonSchemaEntity(**schema.model_dump())
        return entity.is_valid
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid schema\n{str(ex)}")


@router.put("/", status_code=204)
async def create_or_update_schema(
    schema: SchemaDto = Body(..., description="The schema to be created or updated.")
) -> None:
    """
    Create a new schema or update an existing one if the `id` property is provided.
    """
    try:
        if schema.id != None:
            return JSONResponse(
                status_code=500,
                content={"message": "Unsuported update operation"},
            )

        json_schema_entity = JsonSchemaEntity(**schema.json_schema.model_dump())
        if not json_schema_entity.json_schema.is_valid:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid schema"},
            )

        await schema_collection.insert(
            SchemaEntity(id=schema.id, name=schema.name, json_schema=json_schema_entity)
        )
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )
