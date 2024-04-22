from abc import abstractmethod
from typing import Any, Union

from backend.schemas.cohere_chat import CohereChatRequest


class BaseChat:
    """Base for all chat options."""

    @abstractmethod
    def chat(
        self, chat_request: Union[CohereChatRequest, None], **kwargs: Any
    ) -> Any: ...
