from typing import Union

from pydantic import BaseModel


class DocumentBase(BaseModel):
    pass


class Document(BaseModel):
    text: str
    document_id: str

    title: Union[str, None]
    url: Union[str, None]
    fields: Union[dict, None]
    tool_name: Union[str, None]

    class Config:
        from_attributes = True
