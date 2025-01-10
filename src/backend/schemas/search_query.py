from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """
    Schema for search query
    """
    text: str = Field(
        ...,
        title="Text",
        description="Text for the search",
    )
    generation_id: str = Field(
        ...,
        title="Generation ID",
        description="Unique identifier for the generation",
    )

    class Config:
        from_attributes = True
