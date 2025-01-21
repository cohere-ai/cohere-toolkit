from typing import Any

from backend.database_models import (
    COMMUNITY_MODEL_DEPLOYMENTS_MODULE,
    DEFAULT_MODEL_DEPLOYMENTS_MODULE,
)


def class_name_validator(v: str):
    from backend.model_deployments.utils import get_module_class

    deployment_class = get_module_class(DEFAULT_MODEL_DEPLOYMENTS_MODULE, v)
    if not deployment_class:
        deployment_class = get_module_class(COMMUNITY_MODEL_DEPLOYMENTS_MODULE, v)
    if not deployment_class:
        raise ValueError(f"Deployment class not found: {v}")

    return v


def get_deployment_config_var(var_name: str, default: str, **kwargs: Any) -> str:
    """
    Get the Deployment's config, in order of priority:

    1. Request header values
    2. DB values
    3. Default values (from config)

    Args:
        var_name (str): Variable name
        default (str): Variable  default value

    Returns:
        str: Deployment config  value

    """
    ctx = kwargs.get("ctx")
    db_config = kwargs.get("db_config", {})
    config = None

    # Get Request Header value
    ctx_deployment_config = ctx.deployment_config if ctx else {}

    if ctx_deployment_config:
        config = ctx_deployment_config.get(var_name)

    if not config:
        # Check if DB config exists, otherwise use default
        config = db_config.get(var_name, default)

    # After all fallbacks, if config is still invalid
    if not config:
        raise ValueError(f"Missing deployment config variable: {var_name}")

    return config


def get_module_class(module_name: str, class_name: str):
    import importlib

    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls
    except (ImportError, AttributeError):
        cls = None

    return cls


def add_rerank_model_to_request_state(
    model: str,
    **kwargs: Any,
) -> None:
    request = kwargs.get("request", None)
    if not request:
        return
    request.state.rerank_model = model
