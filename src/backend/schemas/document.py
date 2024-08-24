from typing import Optional

from pydantic import BaseModel


class DocumentBase(BaseModel):
    pass


class Document(BaseModel):
    text: Optional[str] = None
    document_id: str

    title: Optional[str] = None
    url: Optional[str] = None
    fields: Optional[dict] = None
    tool_name: Optional[str] = None

    class Config:
        from_attributes = True
