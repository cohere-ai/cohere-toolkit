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


def get_model_config_var(var_name: str, default: str, **kwargs: Any) -> str:
    """Get the model config variable.

    Args:
        var_name (str): Variable name.
        model_config (dict): Model config.

    Returns:
        str: Model config variable value.

    """
    ctx = kwargs.get("ctx")
    model_config = ctx.model_config if ctx else None
    config = (
        model_config[var_name]
        if model_config and model_config.get(var_name)
        else default
    )
    if not config:
        raise ValueError(f"Missing model config variable: {var_name}")
    return config


def get_module_class(module_name: str, class_name: str):
    import importlib

    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls
    except (ImportError, AttributeError) as e:
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
