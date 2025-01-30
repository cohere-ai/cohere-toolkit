import inquirer

from backend.model_deployments.base import BaseDeployment
from backend.scripts.cli.constants import (
    DATABASE_URL_DEFAULT,
    FRONTEND_HOSTNAME_DEFAULT,
    NEXT_PUBLIC_API_HOSTNAME_DEFAULT,
    REDIS_URL_DEFAULT,
    BuildTarget,
    bcolors,
)
from backend.scripts.cli.setters import write_env_file
from backend.scripts.cli.utils import print_styled


def overwrite_config_prompt():
    return inquirer.confirm(
        "Your existing configuration file is invalid. Overwrite?"
    )


def overwrite_secrets_prompt():
    return inquirer.confirm(
        "Your existing secrets file is invalid. Overwrite?"
    )


def core_env_var_prompt(secrets):
    database_url = secrets.get("DATABASE_URL")
    redis_url = secrets.get("REDIS_URL")
    next_public_api_hostname = secrets.get("NEXT_PUBLIC_API_HOSTNAME")
    frontend_hostname = secrets.get("FRONTEND_HOSTNAME")

    if not database_url:
        print_styled("💾 Let's set up your database URL.")
        database_url = inquirer.text(
        "Enter your database URL or press enter for default [recommended]",
            default=DATABASE_URL_DEFAULT,
        )

    if not redis_url:
        print_styled("💾 Now, let's set up need to set up your Redis URL.")
        redis_url = inquirer.text(
            "Enter your Redis URL or press enter for default [recommended]",
            default=REDIS_URL_DEFAULT,
        )

    if not next_public_api_hostname:
        print_styled("💾 Now, let's set up your public backend API hostname.")
        next_public_api_hostname = inquirer.text(
            "Enter your public API Hostname or press enter for default [recommended]",
            default=NEXT_PUBLIC_API_HOSTNAME_DEFAULT,
        )

    if not frontend_hostname:
        print_styled("💾 Finally, the frontend client hostname.")
        frontend_hostname = inquirer.text(
            "Enter your frontend hostname or press enter for default [recommended]",
            default=FRONTEND_HOSTNAME_DEFAULT,
        )

    secrets["DATABASE_URL"] = database_url
    secrets["REDIS_URL"] = redis_url
    secrets["NEXT_PUBLIC_API_HOSTNAME"] = next_public_api_hostname
    secrets["FRONTEND_HOSTNAME"] = frontend_hostname


def deployment_prompt(secrets, configs):
    for secret in configs.env_vars():
        value = secrets.get(secret)

        if not value:
            value = inquirer.text(
                f"Enter the value for {secret}", validate=lambda _, x: len(x) > 0
            )

        secrets[secret] = value


def community_tools_prompt(secrets):
    use_community_features = secrets.get("USE_COMMUNITY_FEATURES")

    if not use_community_features:
        print_styled(
            "🏘️ We have some community tools that you can set up. These tools are not required for the Cohere Toolkit to run."
        )
        use_community_features = inquirer.confirm(
            "Do you want to set up community features (tools and model deployments)?"
        )

    secrets["USE_COMMUNITY_FEATURES"] = use_community_features

    return use_community_features


def tool_prompt(secrets, name, configs):
    print_styled(
        f"🛠️ If you want to enable {name}, set up the following secrets. Otherwise, press enter."
    )

    for key, default_value in configs["secrets"].items():
        value = secrets.get(key)

        if not value:
            value = inquirer.text(f"Enter the value for {key}", default=default_value)

        secrets[key] = value


def build_target_prompt(secrets):
    build_target = secrets.get("BUILD_TARGET")

    if not build_target:
        build_target = inquirer.list_input(
            "Select the build target",
            choices=[BuildTarget.DEV, BuildTarget.PROD],
            default=BuildTarget.DEV,
        )

    secrets["BUILD_TARGET"] = build_target


def review_variables_prompt(secrets):
    review_list = [f"{key}: {value}" for key, value in secrets.items()]

    questions = [
        inquirer.Checkbox(
            "variables",
            message="Review your variables and select the ones you want to update, if any. Press enter to continue",
            choices=review_list,
        ),
    ]

    answers = inquirer.prompt(questions)
    return answers["variables"]


def update_variable_prompt(_, variables_to_update):
    for variable_to_update in variables_to_update:
        variable_to_update = variable_to_update.split(":")[0]
        new_value = inquirer.text(f"Enter the new value for {variable_to_update}")
        write_env_file({variable_to_update: new_value})
        print_styled(
            f"🪛 Updated {variable_to_update} to {new_value}.", bcolors.OKGREEN
        )


def select_deployments_prompt(deployments: dict[str, type[BaseDeployment]], _):
    print_styled("🚀 Let's set up your model deployments.", bcolors.MAGENTA)

    deployments = inquirer.checkbox(
        "Select the model deployments you want to set up",
        choices=[deployment for deployment in deployments.keys()],
        default=["Cohere Platform"],
        validate=lambda _, x: len(x) > 0,
    )
    return deployments


PROMPTS = {
    "core": core_env_var_prompt,
    "build_target": build_target_prompt,
}
