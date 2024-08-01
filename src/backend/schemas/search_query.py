from pydantic import BaseModel


class SearchQueryBase(BaseModel):
    pass


class SearchQuery(BaseModel):
    text: str
    generation_id: str

    class Config:
        from_attributes = True
