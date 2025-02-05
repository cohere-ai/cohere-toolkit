import time
from typing import Any, Callable

from backend.metrics import collector


def track_tool_call_time() -> Callable:
    """
    Decorator to track the execution time of a method and log it to a metrics collector.
    Handles both instance and class methods.
    """
    def decorator(func):
        async def wrapper(self, *args, **kwargs) -> Any:
            class_name = self.__class__.__name__
            passed_method_params = kwargs.get("parameters", {}) or (args[0] if args else {})
            start_time = time.time()
            result = await func(self, *args, **kwargs)
            end_time = time.time()
            time_taken = end_time - start_time
            collector.add_metric('call', 'tool_call', class_name=class_name, method_name='call', method_params=passed_method_params,
                                 latency=time_taken)
            return result

        return wrapper

    return decorator
