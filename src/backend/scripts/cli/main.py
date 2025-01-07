import argparse

from dotenv import dotenv_values

from backend.scripts.cli.constants import (
    COMMUNITY_TOOLS,
    CONFIG_FILE_PATH,
    SECRETS_FILE_PATH,
    TOOLS,
)
from backend.scripts.cli.prompts import (
    PROMPTS,
    community_tools_prompt,
    deployment_prompt,
    overwrite_config_prompt,
    overwrite_secrets_prompt,
    review_variables_prompt,
    select_deployments_prompt,
    tool_prompt,
    update_variable_prompt,
)
from backend.scripts.cli.setters import (
    delete_config_folders,
    write_config_files,
    write_env_file,
    write_template_config_files,
)
from backend.scripts.cli.utils import (
    process_existing_yaml_config,
    show_examples,
    show_welcome_message,
    wrap_up,
)


def start():
    # Set any command args
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-community", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    show_welcome_message()

    secrets = dotenv_values()
    process_existing_yaml_config(secrets, CONFIG_FILE_PATH, overwrite_config_prompt)
    process_existing_yaml_config(secrets, SECRETS_FILE_PATH, overwrite_secrets_prompt)

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

    all_deployments = MANAGED_DEPLOYMENTS_SETUP.copy()
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
