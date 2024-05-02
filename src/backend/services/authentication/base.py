from abc import abstractmethod
from typing import Any


class BaseAuthenticationStrategy:
    """Base strategy for authentication, abstract class that should be inherited from."""

    @abstractmethod
    @staticmethod
    def should_auth_redirect() -> bool: ...

    @abstractmethod
    def login(self, **kwargs: Any): ...

    @abstractmethod
    def authenticate(self, **kwargs: Any): ...