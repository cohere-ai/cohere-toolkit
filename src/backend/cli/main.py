import argparse
import sys
from pathlib import Path

import yaml
from dotenv import dotenv_values

from backend.cli.constants import COMMUNITY_TOOLS, CONFIG_FILE_PATH, TOOLS
from backend.cli.prompts import (
    PROMPTS,
    community_tools_prompt,
    deployment_prompt,
    review_variables_prompt,
    select_deployments_prompt,
    tool_prompt,
    overwrite_config_prompt,
    update_variable_prompt,
)
from backend.cli.setters import (
    convert_yaml_to_secrets,
    delete_config_folders,
    read_yaml,
    write_config_files,
    write_env_file,
    write_template_config_files,
)
from backend.cli.utils import show_examples, show_welcome_message, wrap_up


def start():
    # Set any command args
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-community", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    show_welcome_message()

    secrets = dotenv_values()

    config_file_path = Path(CONFIG_FILE_PATH)

    if config_file_path.is_file():
        try:
            yaml_config = read_yaml(CONFIG_FILE_PATH)
        except yaml.scanner.ScannerError:
            if overwrite_config_prompt():
                yaml_config = {}
                config_file_path.unlink()
            else:
                sys.exit(1)

        yaml_secrets = convert_yaml_to_secrets(yaml_config)
        secrets.update(yaml_secrets)

    # SET UP ENVIRONMENT
    for _, prompt in PROMPTS.items():
        prompt(secrets)

    # ENABLE COMMUNITY TOOLS
    use_community_features = args.use_community and community_tools_prompt(secrets)
    if use_community_features:
        TOOLS.update(COMMUNITY_TOOLS)

    # SET UP TOOLS
    for name, configs in TOOLS.items():
        tool_prompt(secrets, name, configs)

    # SET UP ENVIRONMENT FOR DEPLOYMENTS

    # These imports run code that uses settings. Local imports are used so that we can
    # validate any existing config file above before using settings.
    from backend.config.deployments import (
        AVAILABLE_MODEL_DEPLOYMENTS as MANAGED_DEPLOYMENTS_SETUP,
    )

    from community.config.deployments import (
        AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
    )

    all_deployments = MANAGED_DEPLOYMENTS_SETUP.copy()
    if use_community_features:
        all_deployments.update(COMMUNITY_DEPLOYMENTS_SETUP)

    selected_deployments = select_deployments_prompt(all_deployments, secrets)

    for deployment in selected_deployments:
        deployment_prompt(secrets, all_deployments[deployment])

    # REVIEW VARIABLES
    variables_to_update = review_variables_prompt(secrets)
    update_variable_prompt(secrets, variables_to_update)

    # SET UP .ENV FILE
    write_env_file(secrets)

    # SET UP YAML CONFIG FILES
    # Deal with strange edge case where there are preexisting configuration.yaml
    # and secrets.yaml FOLDERS presents in the config folder - cause still unclear
    delete_config_folders()
    write_template_config_files()
    write_config_files(secrets)

    # WRAP UP
    wrap_up(selected_deployments)

    # SHOW SOME EXAMPLES
    show_examples()


if __name__ == "__main__":
    start()
