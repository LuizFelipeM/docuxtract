from beanie import Document, Indexed


class FileEntity(Document):
    key: Indexed(str)  # type: ignore
    name: str
