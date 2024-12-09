import sys
from pathlib import Path

import yaml

from backend.scripts.cli.constants import (
    ENV_YAML_CONFIG_MAPPING,
    WELCOME_MESSAGE,
    DeploymentName,
    bcolors,
)
from backend.scripts.cli.setters import read_yaml


def print_styled(text: str, color: str = bcolors.ENDC):
    print(color + text + bcolors.ENDC)


def show_welcome_message():
    print_styled(WELCOME_MESSAGE, bcolors.OKGREEN)
    print_styled(
        "👋 First things first, let's set up your environment.", bcolors.MAGENTA
    )


def process_existing_yaml_config(secrets, path, prompt):
    _path = Path(path)

    if _path.is_file():
        try:
            yaml_config = read_yaml(path)
        except yaml.scanner.ScannerError:
            if prompt():
                yaml_config = {}
                _path.unlink()
            else:
                sys.exit(1)

        secrets.update(convert_yaml_to_secrets(yaml_config))


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


def wrap_up(deployments):
    print_styled("✅ Your configuration file has been set up.", bcolors.OKGREEN)

    print_styled(
        "🎉 You're all set up! You can now run `make migrate` and `make dev` to start the Cohere Toolkit. Make sure Docker is running.",
        bcolors.OKGREEN,
    )

    if DeploymentName.SAGE_MAKER in deployments:
        print_styled(
            "🔑 For SageMaker ensure you have run `aws configure` before `make dev` for authentication.",
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
        """\tcurl --location 'http://localhost:8000/v1/chat-stream' --header 'User-Id: test-user' --header 'Content-Type: application/json' --data '{"message": "hey"}'""",
        bcolors.OKCYAN,
    )

    print_styled(
        "3. Ask a question to the SageMaker model",
        bcolors.OKCYAN,
    )
    print_styled(
        """\tcurl --location 'http://localhost:8000/v1/chat-stream' --header 'User-Id: test-user' --header 'Deployment-Name: SageMaker' --header 'Content-Type: application/json' --data '{"message": "hey"}'""",
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
