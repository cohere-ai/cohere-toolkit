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
        REDIRECT_METHOD_NAME (str | None): The router method name that should be used for redirect callback.
    """

    SHOULD_AUTH_REDIRECT = True
    REDIRECT_METHOD_NAME = None

    def __init__subclass(cls, **kwargs):
        super().__init__subclass__(**kwargs)
        if cls.REDIRECT_METHOD_NAME is None:
            raise ValueError(
                f"{cls.__name__} must have a REDIRECT_METHOD_NAME defined, and a corresponding router definition."
            )

    @abstractmethod
    def authenticate(self, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session for OAuth strategies.
        """
        ...
