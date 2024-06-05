import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, computed_field

from backend.schemas.tool import Tool



class AgentBase(BaseModel):
    user_id: str
    # org_id: str

class Agent(AgentBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    version: int
    name: str
    description: Optional[str]
    preamble: Optional[str]
    temperature: float
    # tools: List[Tool]

    model: str
    deployment: str

    class Config:
        from_attributes = True

class UpdateAgent(BaseModel):
    title: Optional[str] = None
    version: Optional[int] = None
    description: Optional[str] = None
    preamble: Optional[str] = None
    temperature: Optional[float] = None
    # tools: Optional[List[Tool]] = None

    class Config:
        from_attributes = True
