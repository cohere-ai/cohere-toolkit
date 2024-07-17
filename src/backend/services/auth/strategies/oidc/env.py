from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OIDCEnvironment(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    oidc_client_id: str = Field(min_length=1)
    oidc_client_secret: str = Field(min_length=1)
    oidc_well_known_endpoint: str = Field(min_length=1)
    frontend_hostname: str = Field(min_length=1)
