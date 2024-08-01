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

ENV_YAML_CONFIG_MAPPING = {
    "USE_COMMUNITY_FEATURES": {
        "type": "config",
        "path": "feature_flags.use_community_features",
    },
    "DATABASE_URL": {"type": "config", "path": "database.url"},
    "REDIS_URL": {"type": "config", "path": "redis.url"},
    # "NEXT_PUBLIC_API_HOSTNAME": "" - this does not exist in Settings() yet to be used for Docker setups,
    "FRONTEND_HOSTNAME": {"type": "config", "path": "auth.frontend_hostname"},
    "PYTHON_INTERPRETER_URL": {
        "type": "config",
        "path": "tools.python_interpreter.url",
    },
    "TAVILY_API_KEY": {"type": "secret", "path": "tools.tavily.api_key"},
    "COHERE_API_KEY": {"type": "secret", "path": "deployments.cohere_platform.api_key"},
    "SAGE_MAKER_ACCESS_KEY": {
        "type": "secret",
        "path": "deployments.sagemaker.access_key",
    },
    "SAGE_MAKER_SECRET_KEY": {
        "type": "secret",
        "path": "deployments.sagemaker.secret_key",
    },
    "SAGE_MAKER_SESSION_TOKEN": {
        "type": "secret",
        "path": "deployments.sagemaker.session_token",
    },
    "SAGE_MAKER_REGION_NAME": {
        "type": "config",
        "path": "deployments.sagemaker.region_name",
    },
    "SAGE_MAKER_ENDPOINT_NAME": {
        "type": "config",
        "path": "deployments.sagemaker.endpoint_name",
    },
    "BEDROCK_ACCESS_KEY": {"type": "secret", "path": "deployments.bedrock.access_key"},
    "BEDROCK_SECRET_KEY": {"type": "secret", "path": "deployments.bedrock.secret_key"},
    "BEDROCK_SESSION_TOKEN": {
        "type": "secret",
        "path": "deployments.bedrock.session_token",
    },
    "BEDROCK_REGION_NAME": {
        "type": "config",
        "path": "deployments.bedrock.region_name",
    },
    "AZURE_API_KEY": {"type": "secret", "path": "deployments.azure.api_key"},
    "AZURE_CHAT_ENDPOINT_URL": {
        "type": "config",
        "path": "deployments.azure.endpoint_url",
    },
    "SINGLE_CONTAINER_URL": {
        "type": "config",
        "path": "deployments.single_container.url",
    },
    "SINGLE_CONTAINER_MODEL": {
        "type": "config",
        "path": "deployments.single_container.model",
    },
}
