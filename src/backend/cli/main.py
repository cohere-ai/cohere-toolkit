import argparse
from enum import StrEnum

import inquirer
from dotenv import set_key

from backend.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS as MANAGED_DEPLOYMENTS_SETUP,
)
from community.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
)
from community.config.tools import COMMUNITY_TOOLS_SETUP


class bcolors:
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    MAGENTA = "\033[35m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class DeploymentName(StrEnum):
    COHERE_PLATFORM = "Cohere Platform"
    SAGE_MAKER = "SageMaker"
    AZURE = "Azure"
    BEDROCK = "Bedrock"


class ToolName(StrEnum):
    PythonInterpreter = "Python Interpreter"
    TavilyInternetSearch = "Tavily Internet Search"


WELCOME_MESSAGE = r"""
 █████╗  █████╗ ██╗  ██╗███████╗██████╗ ███████╗ ████████╗ █████╗  █████╗ ██╗     ██╗  ██╗██╗████████╗
██╔══██╗██╔══██╗██║  ██║██╔════╝██╔══██╗██╔════╝ ╚══██╔══╝██╔══██╗██╔══██╗██║     ██║ ██╔╝██║╚══██╔══╝
██║  ╚═╝██║  ██║███████║█████╗  ██████╔╝█████╗      ██║   ██║  ██║██║  ██║██║     █████═╝ ██║   ██║   
██║  ██╗██║  ██║██╔══██║██╔══╝  ██╔══██╗██╔══╝      ██║   ██║  ██║██║  ██║██║     ██╔═██╗ ██║   ██║   
╚█████╔╝╚█████╔╝██║  ██║███████╗██║  ██║███████╗    ██║   ╚█████╔╝╚█████╔╝███████╗██║ ╚██╗██║   ██║   
 ╚════╝  ╚════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝    ╚═╝    ╚════╝  ╚════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   
"""
DATABASE_URL_DEFAULT = "postgresql+psycopg2://postgres:postgres@db:5432"
PYTHON_INTERPRETER_URL_DEFAULT = "http://terrarium:8080"
NEXT_PUBLIC_API_HOSTNAME_DEFAULT = "http://localhost:8000"

DOT_ENV_FILE_PATH = ".env"


def print_styled(text: str, color: str = bcolors.ENDC):
    print(color + text + bcolors.ENDC)


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


def database_url_prompt(secrets):
    print_styled("💾 We need to set up your database URL.")
    database_url = inquirer.text(
        "Enter your database URL or press enter for default [recommended]",
        default=DATABASE_URL_DEFAULT,
    )

    print_styled("💾 Now, let's set up your public API Hostname")
    next_public_api_hostname = inquirer.text(
        "Enter your public API Hostname or press enter for default [recommended]",
        default=NEXT_PUBLIC_API_HOSTNAME_DEFAULT,
    )

    secrets["DATABASE_URL"] = database_url
    secrets["NEXT_PUBLIC_API_HOSTNAME"] = next_public_api_hostname


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


def write_env_file(secrets):
    for key, value in secrets.items():
        set_key(DOT_ENV_FILE_PATH, key, str(value))


def select_deployments_prompt(deployments, _):
    print_styled("🚀 Let's set up your model deployments.", bcolors.MAGENTA)

    deployments = inquirer.checkbox(
        "Select the model deployments you want to set up",
        choices=[deployment.value for deployment in deployments.keys()],
        default=["Cohere Platform"],
        validate=lambda _, x: len(x) > 0,
    )
    return deployments


def wrap_up(deployments):
    print_styled("✅ Your .env file has been set up.", bcolors.OKGREEN)

    print_styled(
        "🎉 You're all set up! You can now run 'make migrate' and 'make dev' to start the Cohere Toolkit. Make sure Docker is running.",
        bcolors.OKGREEN,
    )

    if DeploymentName.SAGE_MAKER in deployments:
        print_styled(
            "🔑 For SageMaker ensure you have run `aws configure` before make dev for authentication",
            bcolors.OKGREEN,
        )


def show_examples():
    print_styled("📚 Here are some examples to get you started:", bcolors.OKCYAN)

    print_styled(
        "1. Navigate to the Cohere Toolkit frontend: ",
        bcolors.OKCYAN,
    )
    print_styled(
        "\thttp://localhost:4000",
        bcolors.OKCYAN,
    )

    print_styled(
        "2. Ask a question to the Cohere Platform model",
        bcolors.OKCYAN,
    )
    print_styled(
        """\tcurl --location 'http://localhost:8000/chat-stream' --header 'User-Id: test-user' --header 'Content-Type: application/json' --data '{"message": "hey"}'""",
        bcolors.OKCYAN,
    )

    print_styled(
        "3. Ask a question to the SageMaker model",
        bcolors.OKCYAN,
    )
    print_styled(
        """\tcurl --location 'http://localhost:8000/chat-stream' --header 'User-Id: test-user' --header 'Deployment-Name: SageMaker' --header 'Content-Type: application/json' --data '{"message": "hey"}'""",
        bcolors.OKCYAN,
    )

    print_styled(
        "4. List all available models deployments and their models",
        bcolors.OKCYAN,
    )
    print_styled(
        "\tcurl http://localhost:8000/deployments",
        bcolors.OKCYAN,
    )

    print_styled(
        "For more examples, please visit the Cohere Toolkit README.md",
        bcolors.MAGENTA,
    )


IMPLEMENTATIONS = {
    "database_url": database_url_prompt,
}


TOOLS = {
    ToolName.PythonInterpreter: {
        "secrets": {
            "PYTHON_INTERPRETER_URL": PYTHON_INTERPRETER_URL_DEFAULT,
        },
    },
    ToolName.TavilyInternetSearch: {
        "secrets": {
            "TAVILY_API_KEY": None,
        },
    },
}


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-community", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    secrets = {}
    print_styled(WELCOME_MESSAGE, bcolors.OKGREEN)
    print_styled(
        "👋 First things first, let's set up your environment.", bcolors.MAGENTA
    )

    # SET UP ENVIRONMENT
    for _, implementation in IMPLEMENTATIONS.items():
        implementation(secrets)

    # SET UP TOOLS
    use_community_features = args.use_community and community_tools_prompt(secrets)
    if use_community_features:
        TOOLS.update(COMMUNITY_TOOLS_SETUP)

    for name, configs in TOOLS.items():
        tool_prompt(secrets, name, configs)

    # SET UP ENVIRONMENT FOR DEPLOYMENTS
    all_deployments = MANAGED_DEPLOYMENTS_SETUP.copy()
    if use_community_features:
        all_deployments.update(COMMUNITY_DEPLOYMENTS_SETUP)

    selected_deployments = select_deployments_prompt(all_deployments, secrets)

    for deployment in selected_deployments:
        deployment_prompt(secrets, all_deployments[deployment])

    # SET UP .ENV FILE
    write_env_file(secrets)

    # REVIEW VARIABLES
    variables_to_update = review_variables_prompt(secrets)
    update_variable_prompt(secrets, variables_to_update)

    # WRAP UP
    wrap_up(selected_deployments)

    # SHOW SOME EXAMPLES
    show_examples()


if __name__ == "__main__":
    start()
