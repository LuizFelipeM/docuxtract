from beanie import PydanticObjectId
from src.entities.schema_entity import SchemaEntity
from src.views.option_view import OptionView


class SchemasCollection:
    async def get_all(self, user_id: str) -> list[SchemaEntity]:
        return await SchemaEntity.find_many(SchemaEntity.user == user_id).to_list()

    async def get_all_as_options(self, user_id: str) -> list[OptionView]:
        return (
            await SchemaEntity.find_many(SchemaEntity.user == user_id)
            .project(OptionView)
            .to_list()
        )

    async def insert(self, schema: SchemaEntity) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> SchemaEntity:
        return await SchemaEntity.find_one(SchemaEntity.id == PydanticObjectId(id))

    async def find_by_name(self, name: str) -> SchemaEntity:
        return await SchemaEntity.find_one(SchemaEntity.name == name)

    async def has(self, name: str) -> bool:
        return await SchemaEntity.find_one(SchemaEntity.name == name) != None

    async def replace(self, schema: SchemaEntity) -> None:
        await schema.replace()

    async def delete(self, schema: SchemaEntity) -> None:
        await schema.delete()
