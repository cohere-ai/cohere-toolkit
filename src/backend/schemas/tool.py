from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolCategory(StrEnum):
    DataLoader = "Data loader"
    FileLoader = "File loader"
    Function = "Function"
    WebSearch = "Web search"


class Tool(BaseModel):
    name: Optional[str] = ""
    parameter_definitions: Optional[dict] = {}

class ToolDefinition(Tool):
    display_name: str = ""
    description: str = ""
    error_message: Optional[str] = ""
    kwargs: dict = {}
    is_visible: bool = False
    is_available: bool = False
    category: ToolCategory = ToolCategory.DataLoader

    is_auth_required: bool = False  # Per user
    auth_url: Optional[str] = ""  # Per user
    token: Optional[str] = ""  # Per user
    should_return_token: bool = False

    implementation: Any = Field(exclude=True)
    auth_implementation: Any = Field(default=None, exclude=True)

    class Config:
        from_attributes = True


class ToolCall(BaseModel):
    name: str
    parameters: dict = {}

    class Config:
        from_attributes = True


class ToolCallDelta(BaseModel):
    name: str | None
    index: int | None
    parameters: str | None

    class Config:
        from_attributes = True
