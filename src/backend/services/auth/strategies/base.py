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
        PKCE_ENABLED (bool): Whether the strategy can use PKCE.
            Note: If your auth provider does not support PKCE it could break the auth flow.
    """

    NAME = None
    PKCE_ENABLED = False

    def __init__(self, *args, **kwargs):
        self._post_init_check()

    def _post_init_check(self):
        if any(
            [
                self.NAME is None,
            ]
        ):
            raise ValueError(f"{self.__name__} must have NAME attribute defined.")

    @abstractmethod
    def get_client_id(self, **kwargs: Any):
        """
        Retrieves the OAuth app's client ID
        """
        ...

    @abstractmethod
    def get_authorization_endpoint(self, **kwargs: Any):
        """
        Retrieves the OAuth app's authorization endpoint.
        """
        ...

    @abstractmethod
    def get_pkce_enabled(self, **kwargs: Any):
        """
        Retrieves whether the OAuth app supports PKCE and should be enabled
        during authorization.
        """
        ...

    @abstractmethod
    async def get_endpoints(self, **kwargs: Any):
        """
        Retrieves the /token and /userinfo endpoints.
        """
        ...

    @abstractmethod
    async def authorize(self, **kwargs: Any):
        """
        Authentication logic: dealing with user data and returning it
        to set the current user session for OAuth strategies.
        """
        ...
