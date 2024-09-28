import os
from typing import Literal
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


# DatabaseOptions = Literal["template"]

# class MongoClient:
#     def __init__(self, database: DatabaseOptions) -> None:
#         self.database = database

#     def get_session(self) -> AsyncIOMotorDatabase:
#         return client[self.database]
