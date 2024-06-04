from abc import abstractmethod
from typing import Any, List


class BaseAuthenticationStrategy:
    """
    Base strategy for authentication, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
        SHOULD_AUTH_REDIRECT (str): Whether the strategy requires a redirect to the /auth endpoint after login.
    """

    NAME = "Base"
    SHOULD_AUTH_REDIRECT = False

    @staticmethod
    def get_required_payload(self) -> List[str]:
        """
        The required /login payload for the Auth strategy
        """
        ...

    @abstractmethod
    def login(self, **kwargs: Any):
        """
        Login logic: dealing with checking credentials, returning user object
        to store into session if finished. For OAuth strategies, the next step
        will be to authenticate.
        """
        ...


class BaseOAuthStrategy(BaseAuthenticationStrategy):
    """
    Base strategy for OAuth, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
        SHOULD_AUTH_REDIRECT (str): Whether the strategy requires a redirect to the /auth endpoint after login.
    """

    SHOULD_AUTH_REDIRECT = True

    @abstractmethod
    def authenticate(self, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session for OAuth strategies.
        """
        ...
