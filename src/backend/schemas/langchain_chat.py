from backend.schemas.chat import BaseChatRequest


class LangchainChatRequest(BaseChatRequest):
    """
    Request shape for Langchain Streamed Chat.
    """
