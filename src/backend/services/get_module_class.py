# This function is used to get a class from a module by its name.
def get_module_class(module_name: str, class_name: str):
    import importlib

    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls
    except (ImportError, AttributeError) as e:
        cls = None

    return cls
