from beanie import Document, Indexed


class FileModel(Document):
    hash: Indexed(str)  # type: ignore
    name: str


class FileCollection:
    async def insert(self, schema: FileModel) -> str:
        return (await schema.insert()).id

    async def find_by_id(self, id: str) -> FileModel:
        return await FileModel.find_one(FileModel.id == id)

    async def find_by_name(self, name: str) -> FileModel:
        return await FileModel.find_one(FileModel.name == name)

    async def has(self, name: str) -> bool:
        return await FileModel.find_one(FileModel.name == name) != None
