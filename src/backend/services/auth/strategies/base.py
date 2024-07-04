import logging
from abc import abstractmethod
from typing import Any, List

import requests
from starlette.requests import Request


class BaseOAuthStrategy:
    """
    Base strategy for OAuth, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
    """

    NAME = "Base"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._post_init_check()

    def _post_init_check(self):
        if any(
            [
                self.NAME is None,
            ]
        ):
            raise ValueError(
                f"{self.__class__.__name__} must have NAME parameter(s) defined."
            )

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
    def get_refresh_token_params(self, **kwargs: Any):
        """
        Retrieves the OAuth app's refresh token query parameters,
        returned in dict format.
        """
        ...

    async def get_endpoints(self):
        try:
            response = requests.get(self.WELL_KNOWN_ENDPOINT)
            endpoints = response.json()
            self.TOKEN_ENDPOINT = endpoints["token_endpoint"]
            self.USERINFO_ENDPOINT = endpoints["userinfo_endpoint"]
            self.AUTHORIZATION_ENDPOINT = endpoints["authorization_endpoint"]
        except Exception as e:
            logging.error(f"Error while fetching endpoints {e}")
            raise

    async def authorize(self, request: Request) -> dict | None:
        """
        Authorizes and fetches access token ,then retrieves user info.

        Args:
            request (Request): Current request.

        Returns:
            dict: User info.
        """
        try:
            token = self.client.fetch_token(
                url=self.TOKEN_ENDPOINT,
                authorization_response=str(request.url),
                redirect_uri=self.REDIRECT_URI,
            )

            user_info = self.client.get(self.USERINFO_ENDPOINT)

            return user_info.json()
        except Exception as e:
            logging.error(f"Error during authorization: {e}")
            return None

    async def refresh(self, request: Request) -> dict | None:
        """
        Uses refresh token to generate a new access token, then returns user info.

        Args:
            request (Request): Current request.

        Returns:
            Dict: User info.
        """
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            logging.error("Refresh token not found in cookies.")
            return None

        try:
            token = self.client.refresh_token(
                url=self.TOKEN_ENDPOINT,
                refresh_token=refresh_token,
            )

            user_info = self.client.get(self.USERINFO_ENDPOINT)

            return user_info.json()
        except Exception as e:
            logging.error(f"Error during token refresh: {e}")
            raise


class BaseAuthenticationStrategy:
    """
    Base strategy for authentication, abstract class that should be inherited from.

    Attributes:
        NAME (str): The name of the strategy.
    """

    NAME = "Base"

    @staticmethod
    def get_required_payload() -> List[str]:
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
