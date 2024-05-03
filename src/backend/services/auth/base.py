from abc import abstractmethod
from typing import Any, List


class BaseAuthenticationStrategy:
    """
    Base strategy for authentication, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
        SHOULD_ATTACH_TO_APP (str): Whether the strategy needs to be attached to the FastAPI application.
        SHOULD_AUTH_REDIRECT (str): Whether the strategy requires a redirect to the /auth endpoint after login.
    """

    NAME = "Base"
    SHOULD_ATTACH_TO_APP = False
    SHOULD_AUTH_REDIRECT = False

    @staticmethod
    def get_required_payload(self) -> List[str]:
        """
        The required /login payload for the Auth strategy
        """
        ...

    @classmethod
    def login(cls, **kwargs: Any):
        """
        Login logic: dealing with checking credentials.
        """
        ...

    @classmethod
    def authenticate(cls, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session.
        """
        ...
