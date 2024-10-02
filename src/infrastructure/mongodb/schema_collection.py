from src.entities.schema_entity import SchemaEntity


class SchemaCollection:
    async def insert(self, schema: SchemaEntity) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> SchemaEntity:
        return await SchemaEntity.find_one(SchemaEntity.id == id)

    async def find_by_name(self, name: str) -> SchemaEntity:
        return await SchemaEntity.find_one(SchemaEntity.name == name)

    async def has(self, name: str) -> bool:
        return await SchemaEntity.find_one(SchemaEntity.name == name) != None
