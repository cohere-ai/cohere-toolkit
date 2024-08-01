from typing import List

from fastapi import Depends, HTTPException, Request

from backend.chat.custom.custom import CustomChat
from backend.crud import conversation as conversation_crud
from backend.database_models import File as FileModel
from backend.database_models import Message as MessageModel
from backend.database_models.conversation import Conversation as ConversationModel
from backend.database_models.database import DBSessionDep
from backend.schemas.chat import ChatRole
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.schemas.conversation import Conversation
from backend.schemas.file import File
from backend.schemas.message import Message
from backend.services.chat import generate_chat_response
from backend.services.context import get_context
from backend.services.file import attach_conversation_id_to_files, get_file_service

DEFAULT_TITLE = "New Conversation"
GENERATE_TITLE_PROMPT = """# TASK
Given the following conversation history, write a short title that summarizes the topic of the conversation. Be concise and respond with just the title.

## START CHATLOG
%s
## END CHATLOG

# TITLE
"""
SEARCH_RELEVANCE_THRESHOLD = 0.3


def validate_conversation(
    session: DBSessionDep, conversation_id: str, user_id: str
) -> Conversation:
    """Validates if a conversation exists and belongs to the user

    Args:
        session (DBSessionDep): Database session
        conversation_id (str): Conversation ID
        user_id (str): User ID

    Returns:
        ConversationModel: Conversation object

    Raises:
        HTTPException: If the conversation is not found
    """
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )
    return conversation


def extract_details_from_conversation(
    convo: Conversation,
    num_turns: int = 5,
    ignore_system: str = True,
    ignore_tool: str = True,
) -> str:
    """
    Extracts the last num_turns from a conversation, ignoring system and tool messages

    Args:
        convo (Conversation): The conversation object
        num_turns (int): The number of turns to extract
        ignore_system (bool): Whether to ignore system messages
        ignore_tool (bool): Whether to ignore tool messages

    Returns:
        str: The extracted chatlog
    """
    messages = convo.messages
    len_messages = len(messages)
    num_turns = min(len_messages, num_turns)
    start_turn = len_messages - num_turns

    turns = []
    for i in range(start_turn, len_messages):
        message = messages[i]

        # Ignore tool messages
        if ignore_tool and message.agent == ChatRole.TOOL:
            continue

        if ignore_system and message.agent == ChatRole.SYSTEM:
            continue

        # <Role>: <Message>
        turn_str = message.agent + ": " + message.text
        turns.append(turn_str)

    chatlog = "\n".join(turns)
    return chatlog


def get_messages_with_files(
    session: DBSessionDep, user_id: str, messages: list[MessageModel]
) -> list[Message]:
    """
    Get messages and use the file service to get the files associated with each message

    Args:
        session (DBSessionDep): The database session
        user_id (str): The user ID
        messages (list[MessageModel]): The messages to get files for

    Returns:
        list[Message]: The messages with files
    """
    messages_with_file = []

    for message in messages:
        files = get_file_service().get_files_by_message_id(session, message.id, user_id)
        files_with_conversation_id = attach_conversation_id_to_files(
            message.conversation_id, files
        )
        messages_with_file.append(
            Message(
                id=message.id,
                text=message.text,
                created_at=message.created_at,
                updated_at=message.updated_at,
                generation_id=message.generation_id,
                position=message.position,
                is_active=message.is_active,
                files=files_with_conversation_id,
                documents=message.documents,
                citations=message.citations,
                tool_calls=message.tool_calls,
                tool_plan=message.tool_plan,
                agent=message.agent,
            )
        )

    return messages_with_file


def get_documents_to_rerank(conversations: List[Conversation]) -> List[str]:
    """Get documents (strings) to rerank from a list of conversations

    Args:
        conversations (List[Conversation]): List of conversations

    Returns:
        List[str]: List of documents to rerank
    """
    rerank_documents = []
    for conversation in conversations:
        chatlog = extract_details_from_conversation(conversation)

        document = f"Title: {conversation.title}\n"
        if len(chatlog.strip()) != 0:
            document += "\nChatlog:\n{chatlog}"

        rerank_documents.append(document)

    return rerank_documents


async def filter_conversations(
    query: str,
    conversations: List[Conversation],
    rerank_documents: List[str],
    model_deployment,
    ctx: Context,
) -> List[Conversation]:
    """Filter conversations based on the rerank score

    Args:
        query (str): The query to filter conversations
        conversations (List[Conversation]): List of conversations
        rerank_documents (List[str]): List of documents to rerank
        model_deployment: Model deployment object
        ctx (Context): Context object

    Returns:
        List[Conversation]: List of filtered conversations
    """
    # if rerank is not enabled, filter out conversations that don't contain the query
    if not model_deployment.rerank_enabled:
        filtered_conversations = []

        for rerank_document, conversation in zip(rerank_documents, conversations):
            if query.lower() in rerank_document.lower():
                filtered_conversations.append(conversation)

        return filtered_conversations

    # Rerank documents
    res = await model_deployment.invoke_rerank(
        query=query,
        documents=rerank_documents,
        ctx=ctx,
    )

    # Sort conversations by rerank score
    res["results"].sort(key=lambda x: x["relevance_score"], reverse=True)

    # Filter out conversations with low relevance score
    reranked_conversations = [
        conversations[r["index"]]
        for r in res["results"]
        if r["relevance_score"] > SEARCH_RELEVANCE_THRESHOLD
    ]

    return reranked_conversations


async def generate_conversation_title(
    session: DBSessionDep,
    conversation: ConversationModel,
    agent_id: str,
    ctx: Context,
):
    """Generate a title for a conversation

    Args:
        request: Request object
        session: Database session
        conversation: Conversation object
        model_config: Model configuration
        agent_id: Agent ID
        ctx: Context object

    Returns:
        str: Generated title
    """
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()
    title = ""

    try:
        chatlog = extract_details_from_conversation(conversation)
        prompt = GENERATE_TITLE_PROMPT % chatlog
        chat_request = CohereChatRequest(
            message=prompt,
        )

        response = await generate_chat_response(
            session,
            CustomChat().chat(
                chat_request,
                stream=False,
                agent_id=agent_id,
                ctx=ctx,
            ),
            response_message=None,
            conversation_id=None,
            user_id=user_id,
            should_store=False,
            ctx=ctx,
        )

        title = response.text
    except Exception as e:
        title = DEFAULT_TITLE
        logger.error(
            event=f"[Conversation] Error generating title: Conversation ID {conversation.id}, {e}",
        )

    return title
