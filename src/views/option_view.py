from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class OptionView(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str
