import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse

from ..auth.dependencies import get_current_user, validate_token
from ..dtos.json_schema_dto import JsonSchemaDto
from ..dtos.schema_dto import SchemaDto
from ..entities.json_schema_entity import JsonSchemaEntity
from ..entities.schema_entity import SchemaEntity
from src import schemas_collection
from src.logger import logger

router = APIRouter(
    prefix="/schemas", tags=["Schemas"], dependencies=[Depends(validate_token)]
)


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
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=400, detail=f"Invalid schema\n{str(ex)}")


@router.get("/")
async def get_schemas(
    current_user: str = Depends(get_current_user),
) -> list[SchemaDto]:
    try:
        schemaDtos = map(
            lambda schema: SchemaDto(
                id=str(schema.id),
                name=schema.name,
                json_schema=JsonSchemaDto(**schema.json_schema.model_dump()),
            ),
            await schemas_collection.get_all(current_user),
        )
        return list(schemaDtos)
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=500, detail=f"{str(ex)}")


@router.get("/{id}")
async def get_schemas(
    current_user: str = Depends(get_current_user),
    id: str = Path(..., description="The schema id to find."),
) -> SchemaDto:
    try:
        schema = await schemas_collection.find_by_id(id)
        if schema.user != current_user:
            return JSONResponse(
                status_code=403,
                content={"message": f"Schema {id} is not owner by the current user"},
            )

        return SchemaDto(
            id=str(schema.id),
            name=schema.name,
            json_schema=JsonSchemaDto(**schema.json_schema.model_dump()),
        )
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        raise HTTPException(status_code=500, detail=f"{str(ex)}")


@router.put("/", status_code=204)
async def create_or_update_schema(
    current_user: str = Depends(get_current_user),
    schema: SchemaDto = Body(..., description="The schema to be created or updated."),
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
        if not json_schema_entity.is_valid:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid schema"},
            )

        await schemas_collection.insert(
            SchemaEntity(
                id=schema.id,
                user=current_user,
                name=schema.name,
                json_schema=json_schema_entity,
            )
        )
    except Exception as ex:
        logger.log(logging.ERROR, ex)
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )
