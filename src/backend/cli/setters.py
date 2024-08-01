from dotenv import set_key
from backend.cli.constants import (
    BASE_CONFIG_PATH,
    CONFIG_FILE_PATH,
    CONFIG_TEMPLATE_PATH,
    SECRETS_FILE_PATH,
    SECRETS_TEMPLATE_PATH,
    DOT_ENV_FILE_PATH,
)



def write_env_file(secrets):
    for key, value in secrets.items():
        set_key(DOT_ENV_FILE_PATH, key, str(value))

    # Manually set the frontend hostname substitution
    set_key(
        DOT_ENV_FILE_PATH,
        "NEXT_PUBLIC_FRONTEND_HOSTNAME",
        "${FRONTEND_HOSTNAME}",
        "never",
    )

