from abc import abstractmethod
from typing import Any


class BaseAuthenticationStrategy:
    """Base strategy for authentication, abstract class that should be inherited from."""

    @property
    @abstractmethod
    def should_attach_to_app(self) -> bool:
        """
        Whether the Auth strategy needs to be registered with the main
        FastAPI application.
        """
        ...

    @property
    @abstractmethod
    def should_auth_redirect(self) -> bool:
        """
        Whether the Auth strategy requires a redirect to a /auth endpoint
        after the initial login.
        """
        ...

    @abstractmethod
    def login(self, **kwargs: Any):
        """
        Login logic: dealing with checking credentials.
        """
        ...

    @abstractmethod
    def authenticate(self, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session.
        """
        ...
