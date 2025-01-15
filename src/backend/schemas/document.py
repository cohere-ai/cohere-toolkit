from typing import Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Schema for a Document
    """
    text: str = Field(
        ...,
        title="Text",
        description="Document text",
    )
    document_id: str = Field(
        ...,
        title="Document_Id",
        description="Unique Identifier for the document",
    )

    title: Optional[str] = Field(
        None,
        title="Title",
        description="Document title",
    )
    url: Optional[str] = Field(
        None,
        title="URL",
        description="Document URL",
    )
    fields: Optional[dict] = Field(
        None,
        title="Fields",
        description="Document Fields",
    )
    tool_name: Optional[str] = Field(
        None,
        title="Tool Name",
        description="Tool name for the document",
    )

    class Config:
        from_attributes = True
