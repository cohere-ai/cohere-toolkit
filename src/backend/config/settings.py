import sys
from typing import List, Optional, Tuple, Type

from pydantic import AliasChoices, BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

# In order to get the env vars from the top level every model need to inherit from BaseSettings with this config
setting_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    env_nested_delimiter="_",
    env_prefix="",
    env_ignore_empty=True,
)

# To add settings to both YAML and ENV
# First create the nested structure in the YAML file
# Then add the env variables as an AliasChoices in the Field - these aren't nested


class GoogleOAuthSettings(BaseSettings, BaseModel):
    model_config = setting_config
    client_id: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "client_id")
    )
    client_secret: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "client_secret")
    )


class OIDCSettings(BaseSettings, BaseModel):
    model_config = setting_config
    client_id: Optional[str] = Field(
        validation_alias=AliasChoices("OIDC_CLIENT_ID", "client_id")
    )
    client_secret: Optional[str] = Field(
        validation_alias=AliasChoices("OIDC_CLIENT_SECRET", "client_secret")
    )
    well_known_endpoint: Optional[str] = Field(
        validation_alias=AliasChoices("OIDC_WELL_KNOWN_ENDPOINT", "well_known_endpoint")
    )


class AuthSettings(BaseSettings, BaseModel):
    model_config = setting_config
    enabled_auth: Optional[List[str]]
    secret_key: Optional[str] = Field(
        validation_alias=AliasChoices("AUTH_SECRET_KEY", "frontend_hostname")
    )
    frontend_hostname: Optional[str] = Field(
        validation_alias=AliasChoices("FRONTEND_HOSTNAME", "frontend_hostname")
    )
    backend_hostname: Optional[str] = Field(
        validation_alias=AliasChoices("NEXT_PUBLIC_API_HOSTNAME", "backend_hostname")
    )
    oidc: Optional[OIDCSettings]
    google_oauth: Optional[GoogleOAuthSettings]


class FeatureFlags(BaseSettings, BaseModel):
    model_config = setting_config
    use_experimental_langchain: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices(
            "USE_EXPERIMENTAL_LANGCHAIN", "use_experimental_langchain"
        ),
    )
    use_agents_view: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices("USE_AGENTS_VIEW", "use_agents_view"),
    )
    use_community_features: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices(
            "USE_COMMUNITY_FEATURES", "use_community_features"
        ),
    )


class PythonToolSettings(BaseSettings, BaseModel):
    model_config = setting_config
    url: Optional[str] = Field(
        validation_alias=AliasChoices("PYTHON_INTERPRETER_URL", "url")
    )


class CompassSettings(BaseSettings, BaseModel):
    model_config = setting_config
    username: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_COMPASS_USERNAME", "username")
    )
    password: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_COMPASS_PASSWORD", "password")
    )
    api_url: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_COMPASS_API_URL", "api_url")
    )
    parser_url: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_COMPASS_PARSER_URL", "parser_url")
    )


class WebSearchSettings(BaseSettings, BaseModel):
    model_config = setting_config
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("TAVILY_API_KEY", "api_key")
    )


class WolframAlphaSettings(BaseSettings, BaseModel):
    model_config = setting_config
    app_id: Optional[str] = Field(
        validation_alias=AliasChoices("WOLFRAM_APP_ID", "app_id")
    )


class GDriveSettings(BaseSettings, BaseModel):
    model_config = setting_config
    client_id: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_DRIVE_CLIENT_ID", "client_id")
    )
    client_secret: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_DRIVE_CLIENT_SECRET", "client_secret")
    )
    developer_key: Optional[str] = Field(
        validation_alias=AliasChoices(
            "NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY", "developer_key"
        )
    )


class ToolSettings(BaseSettings, BaseModel):
    model_config = setting_config
    enabled_tools: Optional[List[str]]

    python_interpreter: Optional[PythonToolSettings]
    compass: Optional[CompassSettings]
    web_search: Optional[WebSearchSettings]
    wolfram_alpha: Optional[WolframAlphaSettings]
    gdrive: Optional[GDriveSettings]


class DatabaseSettings(BaseSettings, BaseModel):
    model_config = setting_config
    url: Optional[str] = Field(validation_alias=AliasChoices("DATABASE_URL", "url"))
    migrate_token: Optional[str] = Field(
        validation_alias=AliasChoices("MIGRATE_TOKEN", "migrate_token")
    )


class RedisSettings(BaseSettings, BaseModel):
    model_config = setting_config
    url: Optional[str] = Field(validation_alias=AliasChoices("REDIS_URL", "url"))


class SageMakerSettings(BaseSettings, BaseModel):
    model_config = setting_config
    endpoint_name: Optional[str] = Field(
        validation_alias=AliasChoices("SAGE_MAKER_ENDPOINT_NAME", "endpoint_name")
    )
    region_name: Optional[str] = Field(
        validation_alias=AliasChoices("SAGE_MAKER_REGION_NAME", "region_name")
    )
    access_key: Optional[str] = Field(
        validation_alias=AliasChoices("SAGE_MAKER_ACCESS_KEY", "access_key")
    )
    secret_key: Optional[str] = Field(
        validation_alias=AliasChoices("SAGE_MAKER_SECRET_KEY", "secret_key")
    )
    session_token: Optional[str] = Field(
        validation_alias=AliasChoices("SAGE_MAKER_SESSION_TOKEN", "session_token")
    )


class AzureSettings(BaseSettings, BaseModel):
    model_config = setting_config
    endpoint_url: Optional[str] = Field(
        validation_alias=AliasChoices("AZURE_CHAT_ENDPOINT_URL", "endpoint_url")
    )
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("AZURE_API_KEY", "api_key")
    )


class CoherePlatformSettings(BaseSettings, BaseModel):
    model_config = setting_config
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_API_KEY", "api_key")
    )


class SingleContainerSettings(BaseSettings, BaseModel):
    model_config = setting_config
    model: Optional[str] = Field(
        validation_alias=AliasChoices("SINGLE_CONTAINER_MODEL", "model")
    )
    url: Optional[str] = Field(
        validation_alias=AliasChoices("SINGLE_CONTAINER_URL", "url")
    )


class BedrockSettings(BaseSettings, BaseModel):
    model_config = setting_config
    region_name: Optional[str] = Field(
        validation_alias=AliasChoices("BEDROCK_REGION_NAME", "region_name")
    )
    access_key: Optional[str] = Field(
        validation_alias=AliasChoices("BEDROCK_ACCESS_KEY", "access_key")
    )
    secret_key: Optional[str] = Field(
        validation_alias=AliasChoices("BEDROCK_SECRET_KEY", "secret_key")
    )
    session_token: Optional[str] = Field(
        validation_alias=AliasChoices("BEDROCK_SESSION_TOKEN", "session_token")
    )


class DeploymentSettings(BaseSettings, BaseModel):
    model_config = setting_config
    default_deployment: Optional[str]
    enabled_deployments: Optional[List[str]]

    sagemaker: Optional[SageMakerSettings]
    azure: Optional[AzureSettings]
    cohere_platform: Optional[CoherePlatformSettings]
    single_container: Optional[SingleContainerSettings]
    bedrock: Optional[BedrockSettings]


config_file = (
    "src/backend/config/configuration.yaml"
    if "pytest" not in sys.modules
    else "src/backend/tests/configuration.yaml"
)
secrets_file = (
    "src/backend/config/secrets.yaml"
    if "pytest" not in sys.modules
    else "src/backend/tests/secrets.yaml"
)


class Settings(BaseSettings, case_sensitive=False):
    """
    Settings class used to grab environment variables from .env file.
    Uppercase env variables converted to class parameters.
    """

    model_config = setting_config
    auth: Optional[AuthSettings]
    feature_flags: Optional[FeatureFlags]
    tools: Optional[ToolSettings]
    database: Optional[DatabaseSettings]
    redis: Optional[RedisSettings]
    deployments: Optional[DeploymentSettings]

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
        # Below are in prioritized order
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file=config_file),
            YamlConfigSettingsSource(settings_cls, yaml_file=secrets_file),
            file_secret_settings,
            init_settings,
        )
