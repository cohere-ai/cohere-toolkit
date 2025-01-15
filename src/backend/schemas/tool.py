from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolCategory(StrEnum):
    """
    Supported Tool Categories
    """
    DataLoader = "Data loader"
    FileLoader = "File loader"
    Function = "Function"
    WebSearch = "Web search"


class Tool(BaseModel):
    """
    Tool Schema
    """
    name: Optional[str] = Field(
        "",
        title="Name",
        description="Name of the Tool",
    )
    parameter_definitions: Optional[dict] = Field(
        {},
        title="Parameter Definitions",
        description="Parameters definitions for the tool",
    )

class ToolDefinition(Tool):
    """
    Tool Definition Schema
    """
    display_name: str = Field(
        "",
        title="Display Name",
        description="Display name for the tool",
    )
    description: str = Field(
        "",
        title="Description",
        description="Description of the tool",
    )
    error_message: Optional[str] = Field(
        "",
        title="Error Message",
        description="Error message",
    )
    kwargs: dict = Field(
        {},
        title="kwargs",
        description="kwags for the tool",
    )
    is_visible: bool = Field(
        False,
        title="Is Visible",
        description="Is the tool visible",
    )
    is_available: bool = Field(
        False,
        title="Is Available",
        description="Is the tool available",
    )
    category: ToolCategory = Field(
        ToolCategory.DataLoader,
        title="Category",
        description="Tool category",
    )

    is_auth_required: bool = Field(
        False,
        title="Is Auth Required",
        description="Is auth required for the tool",
    )  # Per user
    auth_url: Optional[str] = Field(
        "",
        title="Auth Url",
        description="Auth url for the tool",
    )  # Per user
    token: Optional[str] = Field(
        "",
        title="Token",
        description="Token for the tool",
    )  # Per user
    should_return_token: bool = Field(
        False,
        title="Should Return Token",
        description="If the tool returns a token",
    )

    implementation: Any = Field(
        ...,
        title="Implementation",
        description="Implementation for the tool",
        exclude=True,
    )
    auth_implementation: Optional[Any] = Field(
        None,
        title="Auth Implementation",
        description="Auth implementation for the tool",
        exclude=True,
    )

    class Config:
        from_attributes = True


class ToolCall(BaseModel):
    """
    Schema for Tool Call
    """
    name: str = Field(
        ...,
        title="Name",
        description="Name of the Tool",
    )
    parameters: dict = Field(
        {},
        title="Parameters",
        description="Parameters for the tool call",
    )

    class Config:
        from_attributes = True


class ToolCallDelta(BaseModel):
    """
    Schema for Tool Call Delta
    """
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Name of the Tool",
    )
    index: Optional[int] = Field(
        None,
        title="Index",
        description="Index",
    )
    parameters: Optional[str] = Field(
        None,
        title="Parameters",
        description="Parameters for the tool call",
    )

    class Config:
        from_attributes = True
