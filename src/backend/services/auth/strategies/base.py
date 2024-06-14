from abc import abstractmethod
from typing import Any, List


class BaseAuthenticationStrategy:
    """
    Base strategy for authentication, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
    """

    NAME = "Base"

    @staticmethod
    def get_required_payload(self) -> List[str]:
        """
        The required /login payload for the Auth strategy
        """
        ...

    @abstractmethod
    def login(self, **kwargs: Any):
        """
        Check email/password credentials and return JWT token.
        """
        ...


class BaseOAuthStrategy:
    """
    Base strategy for OAuth, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
        TOKEN_ENDPOINT (str | None): The OAuth token endpoint to validate an authorization code.
        USER_INFO_ENDPOINT (str | None): The OAuth userinfo endpoint to retrieve user data from the access token, after authorization.
    """

    NAME = None
    TOKEN_ENDPOINT = None
    USER_INFO_ENDPOINT = None

    def __init__subclass(cls, **kwargs):
        super().__init__subclass__(**kwargs)
        if any(
            [
                cls.NAME is None,
                cls.TOKEN_ENDPOINT is None,
                cls.USER_INFO_ENDPOINT is None,
            ]
        ):
            raise ValueError(
                f"{cls.__name__} must have NAME, TOKEN_ENDPOINT and USER_INFO_ENDPOINT parameters defined."
            )

    @abstractmethod
    def authorize(self, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session for OAuth strategies.
        """
        ...
