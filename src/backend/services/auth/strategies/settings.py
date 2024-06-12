from pydantic import root_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class used to grab environment variables from .env file.
    Uppercase env variables converted to class parameters.
    """

    class Config:
        env_file = ".env"
        extra = "ignore"

    @root_validator(pre=True)
    def check_required_fields(cls, values):
        # Retrieves list of class properties
        required_fields = list(cls.__annotations__.keys())

        missing_fields = [
            field.upper()
            for field in required_fields
            if field not in values or values[field] is None
        ]

        if missing_fields:
            errors = ", ".join(missing_fields)
            raise ValueError(
                f"Missing required environment variables: {errors}. Please set them in the .env file."
            )

        return values
