import os

import yaml
from dotenv import set_key

from backend.cli.constants import (
    CONFIG_FILE_PATH,
    CONFIG_TEMPLATE_PATH,
    DOT_ENV_FILE_PATH,
    ENV_YAML_CONFIG_MAPPING,
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


def dot_notation_to_nested_dict(flat_dict: dict) -> dict:
    nested_dict = {}

    # Iterate through list of values inorder
    for key, value in flat_dict.items():
        keys = key.split(".")
        d = nested_dict

        # Iterate through dot notation keys inorder, EXCEPT last key
        for subkey in keys[:-1]:
            if subkey not in d:
                d[subkey] = {}
            d = d[subkey]

        # Set last key value
        d[keys[-1]] = value

    return nested_dict


def write_template_config_files():
    if not os.path.exists(CONFIG_FILE_PATH):
        config_template = read_yaml(CONFIG_TEMPLATE_PATH)
        write_yaml(CONFIG_FILE_PATH, config_template)

    if not os.path.exists(SECRETS_FILE_PATH):
        secrets_template = read_yaml(SECRETS_TEMPLATE_PATH)
        write_yaml(SECRETS_FILE_PATH, secrets_template)


def convert_yaml_to_secrets(yaml_dict: dict):
    def get_nested_value(d, path):
        keys = path.split(".")
        value = d
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return None  # Return None if the path does not exist
            value = value[key]
        return value

    secrets = {}
    for env_var, mapping in ENV_YAML_CONFIG_MAPPING.items():
        path = mapping.get("path")
        if path:  # Only process mappings with a defined path
            value = get_nested_value(yaml_dict, path)
            if value is not None:  # Add only if the value exists
                secrets[env_var] = value

    return secrets


def convert_secrets_to_yaml(secrets: dict) -> dict:
    config_changes = {}
    secrets_changes = {}

    for key, value in secrets.items():
        if key in ENV_YAML_CONFIG_MAPPING.keys():
            mapper = ENV_YAML_CONFIG_MAPPING[key]
            type = mapper.get("type")
            path = mapper.get("path")
            if type is None or path is None:
                print(f"Error with YAML config mapping for key {key}.")

            if type == "secret":
                secrets_changes[path] = value
            elif type == "config":
                config_changes[path] = value

    return config_changes, secrets_changes


def write_config_files(secrets: dict):
    config_changes, secrets_changes = convert_secrets_to_yaml(secrets)

    # Make config changes
    if config_changes:
        new_config_data = dot_notation_to_nested_dict(config_changes)
        # Load existing file
        config_data = read_yaml(CONFIG_FILE_PATH)
        # Merge changes
        merge_yaml_dicts(config_data, new_config_data)
        write_yaml(CONFIG_FILE_PATH, config_data)

    # Make secrets changes
    if secrets_changes:
        new_secrets_data = dot_notation_to_nested_dict(secrets_changes)
        # Load existing file
        secrets_data = read_yaml(SECRETS_FILE_PATH)
        # Merge changes
        merge_yaml_dicts(secrets_data, new_secrets_data)
        write_yaml(SECRETS_FILE_PATH, secrets_data)

def delete_config_folders():
    if os.path.isdir(CONFIG_FILE_PATH):
        os.rmdir(CONFIG_FILE_PATH)

    if os.path.isdir(SECRETS_FILE_PATH):
        os.rmdir(SECRETS_FILE_PATH)
