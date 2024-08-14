from backend.cli.constants import WELCOME_MESSAGE, DeploymentName, bcolors


def print_styled(text: str, color: str = bcolors.ENDC):
    print(color + text + bcolors.ENDC)


def show_welcome_message():
    print_styled(WELCOME_MESSAGE, bcolors.OKGREEN)
    print_styled(
        "👋 First things first, let's set up your environment.", bcolors.MAGENTA
    )


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
