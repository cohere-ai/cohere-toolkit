import os

def get_model_config_var(var_name: str, model_config: dict) -> str:
    """Get the model config variable.

    Args:
        var_name (str): Variable name.
        model_config (dict): Model config.

    Returns:
        str: Model config variable value.

    """
    return (
        model_config[var_name]
        if model_config.get(var_name)
        else os.environ.get(var_name)
    )
