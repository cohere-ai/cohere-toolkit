from typing import Any


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
