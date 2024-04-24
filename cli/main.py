from enum import StrEnum

import inquirer
from dotenv import set_key


class bcolors:
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    MAGENTA = "\033[35m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


"""
To add a new deployment, add a new DeploymentName enum and a new entry in the DEPLOYMENTS dictionary containing the secrets required for the deployment.
If the deployment requires a custom implementation, add a new key "custom_implementation" with the function that will be called to set up the deployment.
"""


class DeploymentName(StrEnum):
    COHERE_PLATFORM = "Cohere Platform"
    SAGE_MAKER = "SageMaker"
    AZURE = "Azure"


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
PYTHON_INTERPRETER_URL_DEFAULT = "http://localhost:8080"
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
    for secret in configs["secrets"]:
        if configs.get("custom_implementation"):
            configs["custom_implementation"](secrets)
        else:
            value = inquirer.text(
                f"Enter the value for {secret}", validate=lambda _, x: len(x) > 0
            )
            secrets[secret] = value


def tool_prompt(secrets, name, configs):
    print_styled(
        f"🛠️ If you want to enable {name}, set up the following secrets. Otherwise, press enter."
    )
    for secret in configs["secrets"]:
        value = inquirer.text(f"Enter the value for {secret}")
        secrets[secret] = value


def review_variables_prompt(secrets):
    review_list = [f"{key}: {value}" for key, value in secrets.items()]

    questions = [
        inquirer.Checkbox(
            "variables",
            message="Review your variables and select the ones you want to update, if any",
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
        print_styled(f"🪛 Updated {variable_to_update} to {new_value}.", bcolors.OKGREEN)


def write_env_file(secrets):
    for key, value in secrets.items():
        print_styled(f"🔑 Setting {key} in {DOT_ENV_FILE_PATH} file.")
        set_key(DOT_ENV_FILE_PATH, key, value)


def select_deployments_prompt(_):
    print_styled("🚀 Let's set up your deployments.", bcolors.MAGENTA)

    deployments = inquirer.checkbox(
        "Select the deployments you want to set up",
        choices=[deployment.value for deployment in DeploymentName],
        default=["Cohere Platform"],
        validate=lambda _, x: len(x) > 0,
    )
    return deployments


def wrap_up(deployments):
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
        """\tcurl --location 'http://localhost:8000/chat-stream' --header 'User-Id: test-user' --header 'Deployment: SageMaker' --header 'Content-Type: application/json' --data '{"message": "hey"}'""",
        bcolors.OKCYAN,
    )

    print_styled(
        "4. List all available deployments and their models",
        bcolors.OKCYAN,
    )
    print_styled(
        "\tcurl http://localhost:8000/deployments",
        bcolors.OKCYAN,
    )

    print_styled(
        "For more examples, visit Cohere Toolkit README.md",
        bcolors.MAGENTA,
    )


IMPLEMENTATIONS = {
    "database_url": database_url_prompt,
}


TOOLS = {
    ToolName.PythonInterpreter: {
        "secrets": [
            "PYTHON_INTERPRETER_URL",
        ],
    },
    ToolName.TavilyInternetSearch: {
        "secrets": [
            "TAVILY_API_KEY",
        ],
    },
}


DEPLOYMENTS = {
    DeploymentName.COHERE_PLATFORM: {
        "secrets": [
            "COHERE_API_KEY",
        ],
        "custom_implementation": cohere_api_key_prompt,
    },
    DeploymentName.SAGE_MAKER: {
        "secrets": [
            "SAGE_MAKER_PROFILE_NAME",
            "SAGE_MAKER_REGION_NAME",
            "SAGE_MAKER_ENDPOINT_NAME",
        ],
    },
    DeploymentName.AZURE: {
        "secrets": [
            "AZURE_API_KEY",
            "AZURE_CHAT_ENDPOINT_URL",
        ],
    },
}


def start():
    secrets = {}
    print_styled(WELCOME_MESSAGE, bcolors.OKGREEN)
    print_styled(
        "👋 First things first, let's set up your environment.", bcolors.MAGENTA
    )

    # SET UP ENVIRONMENT
    for _, implementation in IMPLEMENTATIONS.items():
        implementation(secrets)

    # SET UP TOOLS
    for name, configs in TOOLS.items():
        tool_prompt(secrets, name, configs)

    deployments = select_deployments_prompt(secrets)

    # SET UP ENVIRONMENT FOR DEPLOYMENTS
    for deployment in deployments:
        deployment_prompt(secrets, DEPLOYMENTS[deployment])

    # SET UP .ENV FILE
    write_env_file(secrets)

    # REVIEW VARIABLES
    variables_to_update = review_variables_prompt(secrets)
    update_variable_prompt(secrets, variables_to_update)

    print_styled("✅ Your .env file has been set up.", bcolors.OKGREEN)

    # WRAP UP
    wrap_up(deployments)

    # SHOW SOME EXAMPLES
    show_examples()


if __name__ == "__main__":
    start()
