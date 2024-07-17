from functools import cached_property
from logging import Logger
from typing import ClassVar, Optional

import sqlalchemy as sa
from pydantic import Field, ValidationError, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.database_models.database import Database
from backend.services.auth.strategies import (
    GoogleAuthEnvironment,
    GoogleOAuth,
    OIDCEnvironment,
    OpenIDConnect,
)
from backend.services.compass import Compass, CompassEnvironment
from backend.services.logger import get_logger
from backend.tools.google_drive import GCPEnvironment


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="allow", env_nested_delimiter=".", validate_default=True
    )
    logger: ClassVar[Logger] = get_logger("backend.environment")

    # FRONTEND HOSTNAME
    FRONTEND_HOSTNAME: str = Field(min_length=1)

    # COHERE API KEY
    COHERE_API_KEY: str = Field(min_length=1)

    # TAVILY API KEY
    TAVILY_API_KEY: Optional[str] = None

    # GOOGLE DRIVE CREDENTIALS
    GDRIVE_CREDENTIALS: Optional[GCPEnvironment] = None

    # COMPASS CREDENTIALS
    COMPASS_CREDENTIALS: Optional[CompassEnvironment] = None

    @computed_field
    @cached_property
    def COMPASS(self) -> Optional[Compass]:
        try:
            return Compass(
                compass_api_url=self.COMPASS_CREDENTIALS.API_URL,
                compass_parser_url=self.COMPASS_CREDENTIALS.PARSER_URL,
                compass_username=self.COMPASS_CREDENTIALS.USERNAME,
                compass_password=self.COMPASS_CREDENTIALS.PASSWORD,
            )
        except Exception as e:
            raise EnvironmentError(
                "Compass instance could not be configured. Full error log: {}".format(
                    str(e)
                )
            )

    # DB
    DB_DATABASE: str = Field(min_length=1)
    DB_USERNAME: str = Field(min_length=1)
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str = Field(min_length=1)
    DB_PORT: int = Field(ge=0, le=65535)
    DB_RUN_MIGRATIONS: bool = True

    @computed_field
    @cached_property
    def DB_CONNECTION_URL(self) -> sa.URL:
        return sa.URL(
            drivername="postgresql+psycopg2",
            host=self.APOLLO_DB_HOST,
            port=self.APOLLO_DB_PORT,
            query={},
            username=self.APOLLO_DB_USERNAME,
            password=self.APOLLO_DB_PASSWORD,
            database=self.APOLLO_DB_DATABASE,
        )

    @computed_field
    @property
    def db(self) -> Database:
        return Database.create(
            self.APOLLO_DB_CONNECTION_URL, self.APOLLO_DB_RUN_MIGRATIONS
        )

    # OPENID CONNECT
    OPENID_CONNECT_CREDENTIALS: Optional[OIDCEnvironment] = None

    @computed_field
    @cached_property
    def OPENID_CONNECT(self) -> Optional[OpenIDConnect]:
        if self.OPENID_CONNECT_CREDENTIALS:
            return OpenIDConnect(env=self.OPENID_CONNECT_CREDENTIALS)
        return None

    # GOOGLE AUTH
    GOOGLE_AUTH_CREDENTIALS: Optional[GoogleAuthEnvironment] = None

    @computed_field
    @cached_property
    def OPENID_CONNECT(self) -> Optional[OpenIDConnect]:
        if self.GOOGLE_AUTH_CREDENTIALS:
            return GoogleOAuth(env=self.GOOGLE_AUTH_CREDENTIALS)
        return None

    # ERROR HANDLING
    @staticmethod
    def handle_validation_error(e: ValidationError):
        for _e in e.errors():
            _loc = ", ".join(_e["loc"])
            _msg = _e["msg"]
            Configuration.logger.error(f"{_loc}: {_msg}")

        # If we have the inputs, print the keys.
        parsed_fields = [e["input"] for e in e.errors() if e["type"] == "missing"]
        if len(parsed_fields) > 0:
            parsed_fields[0].keys()
            _sorted_fields = ", ".join(sorted(list(parsed_fields[0].keys())))
            Configuration.logger.warning(f"Fields present: {_sorted_fields}")

        raise RuntimeError("Could not validate environment variables.") from None
