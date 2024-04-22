from typing import List

from pydantic import BaseModel


class CitationBase(BaseModel):
    pass


class Citation(BaseModel):
    text: str
    start: int
    end: int
    document_ids: List[str]

    class Config:
        from_attributes = True
