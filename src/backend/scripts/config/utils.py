import yaml


class bcolors:
    FAIL = "\033[91m"
    ENDC = "\033[0m"

def print_styled(text: str, color: str = bcolors.FAIL):
    print(color + text + bcolors.ENDC)

def read_yaml(file_path: str):
    """
    Loads a YAML file.

    Args:
        file_path (str): File path to a YAML file.

    Returns:
        dict: Dictionary representation of the YAML file.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def find_missing_keys(dict_a, dict_b, parent_key=''):
    """
    Recursively checks for keys in dict_b that are missing in dict_a.

    Args:
        dict_a (dict): The base dictionary to compare against.
        dict_b (dict): The dictionary to check for missing keys.
        parent_key (str): Used for tracking nested keys.

    Returns:
        list: A list of missing keys.
    """
    missing_keys = []

    for key, value in dict_b.items():
        # Construct the full key path for nested keys
        full_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, dict):
            # If both dictionaries contain this key, go deeper
            if isinstance(dict_a.get(key), dict):
                missing_keys.extend(find_missing_keys(dict_a[key], value, full_key))
            else:
                # If dict_a has the key but it's not a dictionary, treat all nested keys as missing
                missing_keys.extend(find_missing_keys({}, value, full_key))
        else:
            if key not in dict_a:
                # If the key itself is missing in dict_a
                missing_keys.append(full_key)

    return missing_keys
