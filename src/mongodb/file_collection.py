from src.entities.file_entity import FileEntity


class FileCollection:
    async def insert(self, schema: FileEntity) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> FileEntity:
        return await FileEntity.find_one(FileEntity.id == id)

    async def find_by_key(self, key: str) -> FileEntity:
        return await FileEntity.find_one(FileEntity.key == key)

    async def has(self, key: str) -> bool:
        return await FileEntity.find_one(FileEntity.key == key) != None
