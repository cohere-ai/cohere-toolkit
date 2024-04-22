from backend.schemas.cohere_chat import CohereChatRequest


class LangchainChatRequest(CohereChatRequest):
    """
    Request shape for Langchain Streamed Chat.
    """

    # TODO: add in langchain specific tools
    pass
