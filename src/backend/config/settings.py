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
SETTINGS_CONFIG = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    env_nested_delimiter="_",
    env_prefix="",
    env_ignore_empty=True,
)

CONFIG_PATH = "src/backend/config"
PYTEST_CONFIG_PATH = "src/backend/tests"
CONFIG_FILE_PATH = (
    f"{CONFIG_PATH}/configuration.yaml"
    if "pytest" not in sys.modules
    else f"{PYTEST_CONFIG_PATH}/configuration.yaml"
)
SECRETS_FILE_PATH = (
    f"{CONFIG_PATH}/secrets.yaml"
    if "pytest" not in sys.modules
    else f"{PYTEST_CONFIG_PATH}/secrets.yaml"
)

# To add settings to both YAML and ENV
# First create the nested structure in the YAML file
# Then add the env variables as an AliasChoices in the Field - these aren't nested

class GoogleOAuthSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    client_id: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "client_id")
    ) = None
    client_secret: Optional[str] = Field(
        validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "client_secret")
    ) = None


class OIDCSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
    url: Optional[str] = Field(
        validation_alias=AliasChoices("PYTHON_INTERPRETER_URL", "url")
    )


class CompassSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("TAVILY_API_KEY", "api_key")
    )


class WolframAlphaSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    app_id: Optional[str] = Field(
        validation_alias=AliasChoices("WOLFRAM_APP_ID", "app_id")
    )


class GDriveSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
    enabled_tools: Optional[List[str]]

    python_interpreter: Optional[PythonToolSettings]
    compass: Optional[CompassSettings]
    web_search: Optional[WebSearchSettings]
    wolfram_alpha: Optional[WolframAlphaSettings]
    google_drive: Optional[GDriveSettings]


class DatabaseSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    url: Optional[str] = Field(validation_alias=AliasChoices("DATABASE_URL", "url"))
    migrate_token: Optional[str] = Field(
        validation_alias=AliasChoices("MIGRATE_TOKEN", "migrate_token")
    )


class RedisSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    url: Optional[str] = Field(validation_alias=AliasChoices("REDIS_URL", "url"))


class SageMakerSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
    endpoint_url: Optional[str] = Field(
        validation_alias=AliasChoices("AZURE_CHAT_ENDPOINT_URL", "endpoint_url")
    )
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("AZURE_API_KEY", "api_key")
    )


class CoherePlatformSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    api_key: Optional[str] = Field(
        validation_alias=AliasChoices("COHERE_API_KEY", "api_key")
    )


class SingleContainerSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    model: Optional[str] = Field(
        validation_alias=AliasChoices("SINGLE_CONTAINER_MODEL", "model")
    )
    url: Optional[str] = Field(
        validation_alias=AliasChoices("SINGLE_CONTAINER_URL", "url")
    )


class BedrockSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
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
    model_config = SETTINGS_CONFIG
    default_deployment: Optional[str]
    enabled_deployments: Optional[List[str]]

    sagemaker: Optional[SageMakerSettings]
    azure: Optional[AzureSettings]
    cohere_platform: Optional[CoherePlatformSettings]
    single_container: Optional[SingleContainerSettings]
    bedrock: Optional[BedrockSettings]


class LoggerSettings(BaseSettings, BaseModel):
    model_config = SETTINGS_CONFIG
    level: Optional[str] = Field(
        default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "level")
    )
    strategy: Optional[str] = Field(
        default="structlog", validation_alias=AliasChoices("LOG_STRATEGY", "strategy")
    )
    renderer: Optional[str] = Field(
        default="json", validation_alias=AliasChoices("LOG_RENDERER", "renderer")
    )


class Settings(BaseSettings):
    """
    Settings class used to grab environment variables from .env file.
    Uppercase env variables converted to class parameters.
    """
    model_config = SETTINGS_CONFIG
    auth: Optional[AuthSettings] = None
    feature_flags: Optional[FeatureFlags] = None
    tools: Optional[ToolSettings] = None
    database: Optional[DatabaseSettings] = None
    redis: Optional[RedisSettings] = None
    deployments: Optional[DeploymentSettings] = None
    logger: Optional[LoggerSettings] = None

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
            YamlConfigSettingsSource(settings_cls, yaml_file=CONFIG_FILE_PATH),
            YamlConfigSettingsSource(settings_cls, yaml_file=SECRETS_FILE_PATH),
            file_secret_settings,
            init_settings,
        )
    

