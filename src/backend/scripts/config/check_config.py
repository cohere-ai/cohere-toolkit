from backend.scripts.config.constants import (
    CONFIG_FILE_PATH,
    CONFIG_TEMPLATE_PATH,
    SECRETS_FILE_PATH,
    SECRETS_TEMPLATE_PATH,
)
from backend.scripts.config.utils import find_missing_keys, print_styled, read_yaml


def check_config():
    # Check configuration files
    config_yaml = read_yaml(CONFIG_FILE_PATH)
    config_template_yaml = read_yaml(CONFIG_TEMPLATE_PATH)
    config_keys_missing = find_missing_keys(config_yaml, config_template_yaml)

    # Check secrets files
    secrets_yaml = read_yaml(SECRETS_FILE_PATH)
    secrets_template_yaml = read_yaml(SECRETS_TEMPLATE_PATH)
    secrets_keys_missing = find_missing_keys(secrets_yaml, secrets_template_yaml)

    if config_keys_missing:
        print_styled(f"Warning: Your configuration.yaml is missing the following keys: {config_keys_missing}")

    if secrets_keys_missing:
        print_styled(f"Warning: Your secrets.yaml is missing the following keys: {secrets_keys_missing}")

check_config()
