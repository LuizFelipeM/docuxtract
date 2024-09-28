import asyncio
import os
from beanie import init_beanie
from typing import Literal
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .schema_collection import SchemaCollection, SchemaModel

__all__ = ["SchemaCollection", "load_collection"]


user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

client = AsyncIOMotorClient(
    f"mongodb+srv://{user}:{password}@cluster0.wo4osnm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)


async def load_collection() -> None:
    await init_beanie(database=client.Template, document_models=[SchemaModel])
