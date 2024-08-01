import inquirer

from backend.cli.utils import print_styled
from backend.cli.setters import write_env_file
from backend.cli.constants import (
    bcolors,

    BuildTarget,
    DATABASE_URL_DEFAULT,
    REDIS_URL_DEFAULT,
    NEXT_PUBLIC_API_HOSTNAME_DEFAULT,
    FRONTEND_HOSTNAME_DEFAULT,
    BASE_CONFIG_PATH,
    CONFIG_FILE_PATH,
    CONFIG_TEMPLATE_PATH,
    SECRETS_FILE_PATH,
    SECRETS_TEMPLATE_PATH,
    DOT_ENV_FILE_PATH,
    TOOLS,
)


def cohere_api_key_prompt(secrets):
    key_exists = inquirer.confirm("Do you have a Cohere API key?")
    if key_exists:
        cohere_api_key = inquirer.text(
            "Enter your Cohere API key", validate=lambda _, x: len(x) > 0
        )
    else:
        print_styled(
            "✋ Please visit the following link to get your Cohere API key: https://dashboard.cohere.com/api-keys 🔗",
            bcolors.FAIL,
        )
        cohere_api_key = inquirer.text("Enter your Cohere API key")

    secrets["COHERE_API_KEY"] = cohere_api_key


def core_env_var_prompt(secrets):
    print_styled("💾 Let's set up your database URL.")
    database_url = inquirer.text(
        "Enter your database URL or press enter for default [recommended]",
        default=DATABASE_URL_DEFAULT,
    )

    print_styled("💾 Now, let's set up need to set up your Redis URL.")
    redis_url = inquirer.text(
        "Enter your Redis URL or press enter for default [recommended]",
        default=REDIS_URL_DEFAULT,
    )

    print_styled("💾 Now, let's set up your public backend API hostname.")
    next_public_api_hostname = inquirer.text(
        "Enter your public API Hostname or press enter for default [recommended]",
        default=NEXT_PUBLIC_API_HOSTNAME_DEFAULT,
    )

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
    for secret in configs.env_vars:
        value = inquirer.text(
            f"Enter the value for {secret}", validate=lambda _, x: len(x) > 0
        )
        secrets[secret] = value


def community_tools_prompt(secrets):
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
        value = inquirer.text(f"Enter the value for {key}", default=default_value)
        secrets[key] = value


def build_target_prompt(secrets):
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


def select_deployments_prompt(deployments, _):
    print_styled("🚀 Let's set up your model deployments.", bcolors.MAGENTA)

    deployments = inquirer.checkbox(
        "Select the model deployments you want to set up",
        choices=[deployment.value for deployment in deployments.keys()],
        default=["Cohere Platform"],
        validate=lambda _, x: len(x) > 0,
    )
    return deployments

PROMPTS = {
    "core": core_env_var_prompt,
    "build_target": build_target_prompt,
}