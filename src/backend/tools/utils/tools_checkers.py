from typing import get_args, get_origin

from backend.schemas.tool import ToolCategory, ToolDefinition


def tool_has_category(tool: ToolDefinition, category: ToolCategory) -> bool:
    """
    Check if a tool has a specific category.

    Args:
        tool (ToolDefinition): The tool to check.
        category (ToolCategory): The category to check for.

    Returns:
        bool: True if the tool has the category, False otherwise.
    """
    return tool.category == category


def check_type(param_value, type_description: str) -> bool:
    """
    Check if the parameter value is of the expected type.
    type description is a string representation of the type,
    e.g. "str", "int", "List[str]", "List[Dict[str, int]]", etc.
    For the complex types, we need to parse the string and check the type recursively.

    Args:
        param_value: The value to check.
        type_description: The expected type in string representation.

    Returns:
        bool: True if the value is of the expected type, False otherwise.
    """
    try:
        # Convert the type string into a type object, type description is set by the tool author so no security risk
        expected_type = eval(type_description)
        return _check_type_recursive(param_value, expected_type)
    except Exception as e:
        print(f"Error during type checking: {e}")
        return False


def _check_type_recursive(value, expected_type) -> bool:
    """
    Recursively check the type of the value.
    Types can be base (int, str, ...) or complex (List[str], Dict[str, int], ...).
    So for complex types, we need to check the type recursively.

    Args:
        value: The value to check.
        expected_type: The expected type.

    Returns:
        bool: True if the value is of the expected type, False otherwise.
    """
    origin = get_origin(expected_type)

    if origin is None:  # Base types (int, str, ...)
        return isinstance(value, expected_type)

    if origin is list:  # Check if the value is a list
        if not isinstance(value, list):
            return False
        element_type = get_args(expected_type)[0]
        return all(_check_type_recursive(item, element_type) for item in value)

    if origin is tuple:  # Tuples
        # trying to help to model with tuple type by converting lists to tuples, Cohere model passed tuples as list
        converted_value = tuple(value) if isinstance(value, list) else value
        # Check if the value is a tuple and has the same length as the expected type
        if not isinstance(converted_value, tuple) or len(converted_value) != len(get_args(expected_type)):
            return False
        return all(
            _check_type_recursive(item, arg_type)
            for item, arg_type in zip(value, get_args(expected_type))
        )

    if origin is dict:  # Dictionaries
        if not isinstance(value, dict):
            return False
        key_type, value_type = get_args(expected_type)
        return all(
            _check_type_recursive(k, key_type) and _check_type_recursive(v, value_type)
            for k, v in value.items()
        )

    # NOTE: Maybe we need to handle more types in the future, depends on the use in tools and models
    return False


def check_tool_parameters(tool_definition: ToolDefinition) -> None:
    """
    Decorator to check the parameters of a tool that was passed to a method by the model.

    Args:
        tool_definition (ToolDefinition): The tool definition to check the parameters against.

    Raises:
        ValueError: If a required parameter is missing.
        TypeError: If a parameter has an invalid type.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            parameter_definitions = tool_definition(self).parameter_definitions
            passed_method_params = kwargs.get("parameters", {}) or args[0]
            # Validate parameters
            for param, rules in parameter_definitions.items():
                is_required = rules.get("required", False)
                if param not in passed_method_params:
                    if is_required:
                        raise ValueError(f"Model didn't pass required parameter: {param}")
                else:
                    value = passed_method_params[param]
                    if not value and is_required:
                        raise ValueError(f"Model passed empty value for required parameter: {param}")
                    if not check_type(value, rules["type"]):
                        raise TypeError(
                            f"Model passed invalid parameter. Parameter '{param}' must be of type {rules['type']}, but got {type(value).__name__}"
                        )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
