from typing import Union

from pydantic import BaseModel


class ArcadiaUpdateItem(BaseModel):
    data_key: str
    new_data_key: Union[str, None] = None
    title: str
    tags: list[str]
    description: str
    image_location: str

class ArcadiaAddItem(BaseModel):
    data_key: str
    tags: list[str]
