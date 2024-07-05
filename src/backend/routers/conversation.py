import logging

from fastapi import APIRouter
from fastapi import File as RequestFile
from fastapi import Form, HTTPException, Request
from fastapi import UploadFile as FastAPIUploadFile

from backend.chat.custom.custom import CustomChat
from backend.chat.custom.utils import get_deployment
from backend.config.routers import RouterName
from backend.crud import conversation as conversation_crud
from backend.crud import file as file_crud
from backend.database_models import Conversation as ConversationModel
from backend.database_models import File as FileModel
from backend.database_models.database import DBSessionDep
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.conversation import (
    Conversation,
    ConversationWithoutMessages,
    DeleteConversation,
    GenerateTitle,
    UpdateConversation,
)
from backend.schemas.file import DeleteFile, File, ListFile, UpdateFile, UploadFile
from backend.services.auth.utils import get_header_user_id
from backend.services.chat import generate_chat_response, get_deployment_config
from backend.services.conversation import (
    DEFAULT_TITLE,
    GENERATE_TITLE_PROMPT,
    SEARCH_RELEVANCE_THRESHOLD,
    extract_details_from_conversation,
)
from backend.services.file.service import FileService
from backend.tools.files import get_file_content

router = APIRouter(
    prefix="/v1/conversations",
)
router.name = RouterName.CONVERSATION


# CONVERSATIONS
@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str, session: DBSessionDep, request: Request
) -> Conversation:
    """ "
    Get a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        Conversation: Conversation with the given ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    return conversation


@router.get("", response_model=list[ConversationWithoutMessages])
async def list_conversations(
    *,
    offset: int = 0,
    limit: int = 100,
    agent_id: str = None,
    session: DBSessionDep,
    request: Request,
) -> list[ConversationWithoutMessages]:
    """
    List all conversations.

    Args:
        offset (int): Offset to start the list.
        limit (int): Limit of conversations to be listed.
        agent_id (str): Query parameter for agent ID to optionally filter conversations by agent.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        list[ConversationWithoutMessages]: List of conversations.
    """
    user_id = get_header_user_id(request)

    return conversation_crud.get_conversations(
        session, offset=offset, limit=limit, user_id=user_id, agent_id=agent_id
    )


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    new_conversation: UpdateConversation,
    session: DBSessionDep,
    request: Request,
) -> Conversation:
    """
    Update a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        new_conversation (UpdateConversation): New conversation data.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        Conversation: Updated conversation.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    conversation = conversation_crud.update_conversation(
        session, conversation, new_conversation
    )

    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str, session: DBSessionDep, request: Request
) -> DeleteConversation:
    """
    Delete a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        DeleteConversation: Empty response.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    conversation_crud.delete_conversation(session, conversation_id, user_id)

    return DeleteConversation()


@router.get(":search", response_model=list[ConversationWithoutMessages])
async def search_conversations(
    query: str,
    session: DBSessionDep,
    request: Request,
    offset: int = 0,
    limit: int = 100,
    agent_id: str = None,
) -> list[ConversationWithoutMessages]:
    """
    Search conversations by title.

    Args:
        query (str): Query string to search for in conversation titles.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        list[ConversationWithoutMessages]: List of conversations that match the query.
    """
    user_id = get_header_user_id(request)
    deployment_name = request.headers.get("Deployment-Name", "")
    model_deployment = get_deployment(deployment_name)
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else None

    conversations = conversation_crud.get_conversations(
        session, offset=offset, limit=limit, user_id=user_id, agent_id=agent_id
    )

    if not conversations:
        return []

    rerank_documents = []
    for conversation in conversations:
        chatlog = extract_details_from_conversation(conversation)

        document = f"Title: {conversation.title}\n"
        if len(chatlog.strip()) != 0:
            document += "\nChatlog:\n{chatlog}"

        rerank_documents.append(document)

    # if rerank is not enabled, filter out conversations that don't contain the query
    if not model_deployment.rerank_enabled:
        filtered_conversations = []

        for rerank_document, conversation in zip(rerank_documents, conversations):
            if query.lower() in rerank_document.lower():
                filtered_conversations.append(conversation)

        return filtered_conversations

    # Rerank documents
    res = model_deployment.invoke_rerank(
        query=query,
        documents=rerank_documents,
        user_id=user_id,
        agent_id=agent_id,
        trace_id=trace_id,
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


# FILES
@router.post("/upload_file", response_model=UploadFile)
async def upload_file(
    session: DBSessionDep,
    request: Request,
    conversation_id: str = Form(None),
    file: FastAPIUploadFile = RequestFile(...),
) -> UploadFile:
    """
    Uploads and creates a File object.
    If no conversation_id is provided, a new Conversation is created as well.

    Args:
        session (DBSessionDep): Database session.
        file (FastAPIUploadFile): File to be uploaded.
        conversation_id (Optional[str]): Conversation ID passed from request query parameter.

    Returns:
        UploadFile: Uploaded file.

    Raises:
        HTTPException: If the conversation with the given ID is not found. Status code 404.
        HTTPException: If the file wasn't uploaded correctly. Status code 500.
    """

    user_id = get_header_user_id(request)

    # Create new conversation
    if not conversation_id:
        conversation = conversation_crud.create_conversation(
            session,
            ConversationModel(user_id=user_id),
        )
    # Check for existing conversation
    else:
        conversation = conversation_crud.get_conversation(
            session, conversation_id, user_id
        )

        # Fail if user_id is not provided when conversation DNE
        if not conversation:
            if not user_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"user_id is required if no valid conversation is provided.",
                )

            # Create new conversation
            conversation = conversation_crud.create_conversation(
                session,
                ConversationModel(user_id=user_id),
            )

    # Handle uploading File
    file_path = FileService().upload_file(file)

    # Raise exception if file wasn't uploaded
    if not file_path.exists():
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file {file.filename}."
        )

    try:
        # Read file content
        content = get_file_content(file_path)

        # Create File
        upload_file = FileModel(
            user_id=conversation.user_id,
            conversation_id=conversation.id,
            file_name=file_path.name,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            file_content=content,
        )

        upload_file = file_crud.create_file(session, upload_file)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file {file.filename}."
        )
    finally:
        # Remove local file
        FileService().delete_file(file_path)

    return upload_file


@router.get("/{conversation_id}/files", response_model=list[ListFile])
async def list_files(
    conversation_id: str, session: DBSessionDep, request: Request
) -> list[ListFile]:
    """
    List all files from a conversation. Important - no pagination support yet.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.

    Returns:
        list[ListFile]: List of files from the conversation.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    files = file_crud.get_files_by_conversation_id(session, conversation_id, user_id)
    return files


@router.put("/{conversation_id}/files/{file_id}", response_model=File)
async def update_file(
    conversation_id: str,
    file_id: str,
    new_file: UpdateFile,
    session: DBSessionDep,
    request: Request,
) -> File:
    """
    Update a file by ID.

    Args:
        conversation_id (str): Conversation ID.
        file_id (str): File ID.
        new_file (UpdateFile): New file data.
        session (DBSessionDep): Database session.

    Returns:
        File: Updated file.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    file = file_crud.get_file(session, file_id, user_id)

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} not found.",
        )

    file = file_crud.update_file(session, file, new_file)

    return file


@router.delete("/{conversation_id}/files/{file_id}")
async def delete_file(
    conversation_id: str, file_id: str, session: DBSessionDep, request: Request
) -> DeleteFile:
    """
    Delete a file by ID.

    Args:
        conversation_id (str): Conversation ID.
        file_id (str): File ID.
        session (DBSessionDep): Database session.

    Returns:
        DeleteFile: Empty response.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    file = file_crud.get_file(session, file_id, user_id)

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} not found.",
        )

    # Delete File from local volume, and also the File DB object
    FileService().delete_file(file.file_path)
    file_crud.delete_file(session, file_id, user_id)

    return DeleteFile()


# MISC
@router.post("/{conversation_id}/generate-title", response_model=GenerateTitle)
async def generate_title(
    conversation_id: str, session: DBSessionDep, request: Request
) -> GenerateTitle:
    """
    Generate a title for a conversation and update the conversation with the generated title.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.

    Returns:
        str: Generated title for the conversation.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    agent_id = conversation.agent_id if conversation.agent_id else None
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else None
    deployment_name = request.headers.get("Deployment-Name", "")
    model_config = (
        get_deployment_config(request)
        if request.headers.get("Deployment-Config", "") != ""
        else {}
    )

    title = ""
    try:
        chatlog = extract_details_from_conversation(conversation)
        prompt = GENERATE_TITLE_PROMPT % chatlog
        chat_request = CohereChatRequest(
            message=prompt,
        )

        response = generate_chat_response(
            session,
            CustomChat().chat(
                chat_request,
                stream=False,
                deployment_name=deployment_name,
                deployment_config=model_config,
                trace_id=trace_id,
                user_id=user_id,
                agent_id=agent_id,
            ),
            response_message=None,
            conversation_id=None,
            user_id=user_id,
            should_store=False,
        )

        title = response.text
    except Exception as e:
        title = DEFAULT_TITLE
        logging.error(f"Error generating title for conversation {conversation_id}: {e}")

    conversation_crud.update_conversation(
        session, conversation, UpdateConversation(title=title)
    )

    return GenerateTitle(title=title)
