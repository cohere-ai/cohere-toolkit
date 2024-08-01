from enum import StrEnum


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


class BuildTarget(StrEnum):
    DEV = "dev"
    PROD = "prod"


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
REDIS_URL_DEFAULT = "redis://:redis@redis:6379"
PYTHON_INTERPRETER_URL_DEFAULT = "http://terrarium:8080"
NEXT_PUBLIC_API_HOSTNAME_DEFAULT = "http://localhost:8000"
FRONTEND_HOSTNAME_DEFAULT = "http://localhost:4000"

BASE_CONFIG_PATH = "src/backend/config"
CONFIG_FILE_PATH = f"{BASE_CONFIG_PATH}/configuration.yaml"
CONFIG_TEMPLATE_PATH = f"{BASE_CONFIG_PATH}/configuration.template.yaml"
SECRETS_FILE_PATH = f"{BASE_CONFIG_PATH}/secrets.yaml"
SECRETS_TEMPLATE_PATH = f"{BASE_CONFIG_PATH}/secrets.template.yaml"
DOT_ENV_FILE_PATH = ".env"


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
