from typing import Tuple, Type

from pydantic import AliasChoices, BaseModel, Field, ValidationError
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

setting_config = SettingsConfigDict(env_file=".env", extra="ignore", env_nested_delimiter="_", env_prefix="")
 

class OIDCSettings(BaseSettings, BaseModel):
    model_config = setting_config
    client_id: str
    client_secret: str = Field(validation_alias= AliasChoices('OIDC_CLIENT_SECRET', 'client_secret'))
    well_known_endpoint: str 


class AuthSettings(BaseSettings, BaseModel):
    model_config = setting_config
    frontend_hostname: str
    oidc: OIDCSettings


class Settings(BaseSettings, case_sensitive=False):
    """
    Settings class used to grab environment variables from .env file.
    Uppercase env variables converted to class parameters.
    """
    model_config = setting_config
    auth: AuthSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # The YAML files have to be separate vs in a list as they have the same nested structure
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(
                settings_cls, yaml_file="src/backend/config/configuration.yaml"
            ),
            YamlConfigSettingsSource(
                settings_cls, yaml_file="src/backend/config/secrets.yaml"
            ),
            file_secret_settings,
        )
