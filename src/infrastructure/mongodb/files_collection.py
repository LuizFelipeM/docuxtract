from src.entities.file_entity import FileEntity


class FilesCollection:
    async def insert(self, schema: FileEntity) -> str:
        return (await FileEntity.insert_one(schema)).id

    async def update(self, schema: FileEntity) -> str:
        return (await FileEntity.update(schema)).id

    async def find_by_id(self, id: str) -> FileEntity:
        return await FileEntity.find_one(FileEntity.id == id)

    async def find_by_key(self, key: str) -> FileEntity:
        return await FileEntity.find_one(FileEntity.key == key)

    async def has(self, key: str) -> bool:
        return await FileEntity.find_one(FileEntity.key == key) != None

    async def delete(self, key: str) -> None:
        file = await self.find_by_key(key)
        await FileEntity.delete(file)

    async def delete(self, file: FileEntity) -> None:
        await FileEntity.delete(file)
