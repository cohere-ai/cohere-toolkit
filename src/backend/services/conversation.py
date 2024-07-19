from backend.database_models import Message as MessageModel
from backend.database_models.conversation import Conversation
from backend.database_models.database import DBSessionDep
from backend.schemas.chat import ChatRole
from backend.schemas.message import Message
from backend.services.file import FileService, get_file_content

DEFAULT_TITLE = "New Conversation"
GENERATE_TITLE_PROMPT = """# TASK
Given the following conversation history, write a short title that summarizes the topic of the conversation. Be concise and respond with just the title.

## START CHATLOG
%s
## END CHATLOG

# TITLE
"""
SEARCH_RELEVANCE_THRESHOLD = 0.3

file_service = FileService(session=DBSessionDep)


def extract_details_from_conversation(
    convo: Conversation,
    num_turns: int = 5,
    ignore_system: str = True,
    ignore_tool: str = True,
) -> str:
    """Extracts the last num_turns from a conversation, ignoring system and tool messages

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


def getMessagesWithFiles(
    session: DBSessionDep, user_id: str, messages: list[MessageModel]
) -> list[Message]:
    messages_with_file = []

    for message in messages:
        files = file_service.get_message_files(session, message.id, user_id)
        messages_with_file.append(
            Message(
                id=message.id,
                text=message.text,
                created_at=message.created_at,
                updated_at=message.updated_at,
                generation_id=message.generation_id,
                position=message.position,
                is_active=message.is_active,
                files=files,
                documents=message.documents,
                citations=message.citations,
                tool_calls=message.tool_calls,
                tool_plan=message.tool_plan,
                agent=message.agent,
            )
        )

    return messages_with_file
