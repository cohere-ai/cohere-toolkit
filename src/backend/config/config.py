# need to ignore the yaml files
# have template files
# fix the CLI
# fix docker and deployments
import os
from distutils.util import strtobool

import yaml


# TODO have enabling different deployments, tools, auth configs
class Configuration:
    secrets = dict()
    configuration = dict()
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "secrets.yaml")) as f:
        secrets.update(yaml.load(f, Loader=yaml.FullLoader))
    with open(os.path.join(here, "configuration.yaml")) as f:
        configuration.update(yaml.load(f, Loader=yaml.FullLoader))

    database_config = secrets["database"] | configuration["database"]
    feature_flags = configuration["feature_flags"]
    auth_config = secrets["auth"] | configuration["auth"]
    deployment_config = configuration["deployments"]
    tool_config = configuration["tools"]

    @classmethod
    def get_auth_config(cls, auth_name: str) -> dict:
        return cls.merge_configs("auth", auth_name)

    @classmethod
    def get_deployment_config(cls, deployment_name: str) -> dict:
        return cls.merge_configs("deployments", deployment_name)

    @classmethod
    def get_tool_config(cls, tool_name: str) -> dict:
        return cls.merge_configs("tools", tool_name)

    @classmethod
    def merge_configs(cls, config_name: str, filter_name: str) -> dict:
        config = (
            cls.configuration.get(config_name).get(filter_name)
            if cls.configuration.get(config_name) is not None
            else None
        )
        secrets = (
            cls.secrets.get(config_name).get(filter_name)
            if cls.secrets.get(config_name) is not None
            else None
        )
        # If we have secrets as well as config combine them
        # Otherwise return the one that is not None
        if config is not None and secrets is not None:
            return config | secrets
        return config if config else secrets


def get_config_value(config: dict, config_name: str, env_var: str) -> str:
    return (
        config.get(config_name) if config.get(config_name) else os.environ.get(env_var)
    )


def get_feature_flag(flag_name: str, env_name: str, default: bool) -> bool:
    return False
    config_value = get_config_value(
        Configuration.feature_flags, flag_name, os.getenv(env_name)
    )
    if config_value is not None:
        return bool(strtobool(config_value))
    return default
