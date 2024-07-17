from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CompassEnvironment(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    API_URL: str = Field(min_length=1)
    PARSER_URL: str = "{}/parse".format(API_URL)
    USERNAME: str = ""
    PASSWORD: str = ""
