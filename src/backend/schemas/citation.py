from pydantic import BaseModel, Field


class Citation(BaseModel):
    """
    Schema for a citation
    """
    text: str = Field(
        ...,
        title="Text",
        description="Citation text",
    )
    start: int = Field(
        ...,
        title="Start",
        description="Start position for the citation",
    )
    end: int = Field(
        ...,
        title="End",
        description="End position for the citation",
    )
    document_ids: list[str] = Field(
        ...,
        title="Document IDs",
        description="Documents used for the citation",
    )

    class Config:
        from_attributes = True
