import yaml
from dotenv import set_key

from backend.cli.constants import (
    BASE_CONFIG_PATH,
    CONFIG_FILE_PATH,
    CONFIG_TEMPLATE_PATH,
    DOT_ENV_FILE_PATH,
    SECRETS_FILE_PATH,
    SECRETS_TEMPLATE_PATH,
)

# Use representer to allow writing literal empty value
# https://stackoverflow.com/questions/30134110/how-can-i-output-blank-value-in-python-yaml-file
yaml.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar("tag:yaml.org,2002:null", ""),
)


def write_env_file(secrets: dict):
    for key, value in secrets.items():
        set_key(DOT_ENV_FILE_PATH, key, str(value))

    # Manually set the frontend hostname substitution
    set_key(
        DOT_ENV_FILE_PATH,
        "NEXT_PUBLIC_FRONTEND_HOSTNAME",
        "${FRONTEND_HOSTNAME}",
        "never",
    )


def read_yaml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def write_yaml(file_path: str, data: dict):
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def merge_yaml_dicts(old: dict, new: dict):
    for key, new_value in new.items():
        # Deal with nested dictionary
        if isinstance(new_value, dict) and key in old:
            merge_yaml_dicts(old[key], new_value)
        else:
            old[key] = new_value


def write_template_config_files():
    # Load templates
    config_template = read_yaml(CONFIG_TEMPLATE_PATH)
    secrets_template = read_yaml(SECRETS_TEMPLATE_PATH)

    # Write to files
    write_yaml(CONFIG_FILE_PATH, config_template)
    write_yaml(SECRETS_FILE_PATH, secrets_template)


def write_config_files():
    pass
