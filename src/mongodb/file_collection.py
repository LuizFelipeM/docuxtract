from beanie import Document, Indexed


class FileModel(Document):
    key: Indexed(str)  # type: ignore
    name: str


class FileCollection:
    async def insert(self, schema: FileModel) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> FileModel:
        return await FileModel.find_one(FileModel.id == id)

    async def find_by_key(self, key: str) -> FileModel:
        return await FileModel.find_one(FileModel.key == key)

    async def has(self, key: str) -> bool:
        return await FileModel.find_one(FileModel.key == key) != None
