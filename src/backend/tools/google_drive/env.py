from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GCPEnvironment(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    CLIENT_ID: str = Field(min_length=1)
    CLIENT_SECRET: str = Field(min_length=1)
