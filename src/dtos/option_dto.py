from pydantic import BaseModel


class OptionDto(BaseModel):
    id: str
    label: str
