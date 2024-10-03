from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from src.entities.file_entity import FileEntity
from src.entities.schema_entity import SchemaEntity
from .files_collection import FilesCollection
from .schemas_collection import SchemasCollection

__all__ = ["SchemasCollection", "FilesCollection", "load_collection", "MongoConfig"]


class MongoConfig(BaseModel):
    user: str
    password: str


async def load_collection(config: MongoConfig) -> None:
    client = AsyncIOMotorClient(
        f"mongodb+srv://{config.user}:{config.password}@cluster0.wo4osnm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )

    await init_beanie(
        database=client.Template, document_models=[SchemaEntity, FileEntity]
    )
