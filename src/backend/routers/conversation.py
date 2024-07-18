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
    ConversationPublic,
    ConversationWithoutMessages,
    DeleteConversationResponse,
    GenerateTitleResponse,
    UpdateConversationRequest,
)
from backend.schemas.file import (
    DeleteFileResponse,
    FilePublic,
    ListFile,
    UpdateFileRequest,
    UploadFileResponse,
)
from backend.services.auth.utils import get_header_user_id
from backend.services.chat import generate_chat_response, get_deployment_config
from backend.services.conversation import (
    DEFAULT_TITLE,
    GENERATE_TITLE_PROMPT,
    extract_details_from_conversation,
    filter_conversations,
    generate_conversation_title,
    get_documents_to_rerank,
    validate_conversation,
)
from backend.services.file import (
    get_file_content,
    validate_batch_file_size,
    validate_file,
    validate_file_size,
)

router = APIRouter(
    prefix="/v1/conversations",
)
router.name = RouterName.CONVERSATION


# CONVERSATIONS
@router.get("/{conversation_id}", response_model=ConversationPublic)
async def get_conversation(
    conversation_id: str, session: DBSessionDep, request: Request
) -> ConversationPublic:
    """
    Get a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        ConversationPublic: Conversation with the given ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = validate_conversation(session, conversation_id, user_id)
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


@router.put("/{conversation_id}", response_model=ConversationPublic)
async def update_conversation(
    conversation_id: str,
    new_conversation: UpdateConversationRequest,
    session: DBSessionDep,
    request: Request,
) -> ConversationPublic:
    """
    Update a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        new_conversation (UpdateConversationRequest): New conversation data.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        ConversationPublic: Updated conversation.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    conversation = validate_conversation(session, conversation_id, user_id)

    conversation = conversation_crud.update_conversation(
        session, conversation, new_conversation
    )

    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str, session: DBSessionDep, request: Request
) -> DeleteConversationResponse:
    """
    Delete a conversation by ID.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        DeleteConversationResponse: Empty response.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    _ = validate_conversation(session, conversation_id, user_id)

    conversation_crud.delete_conversation(session, conversation_id, user_id)

    return DeleteConversationResponse()


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

    rerank_documents = get_documents_to_rerank(conversations)
    filtered_documents = await filter_conversations(
        query,
        conversations,
        rerank_documents,
        model_deployment,
        user_id,
        agent_id,
        trace_id,
    )

    return filtered_documents


# FILES
# TODO: Deprecate singular file upload once client uses batch upload endpoint
@router.post("/upload_file", response_model=UploadFileResponse)
async def upload_file(
    session: DBSessionDep,
    request: Request,
    conversation_id: str = Form(None),
    file: FastAPIUploadFile = RequestFile(...),
) -> UploadFileResponse:
    """
    Uploads and creates a File object.
    If no conversation_id is provided, a new Conversation is created as well.

    Args:
        session (DBSessionDep): Database session.
        file (FastAPIUploadFile): File to be uploaded.
        conversation_id (Optional[str]): Conversation ID passed from request query parameter.

    Returns:
        UploadFileResponse: Uploaded file.

    Raises:
        HTTPException: If the conversation with the given ID is not found. Status code 404.
        HTTPException: If the file wasn't uploaded correctly. Status code 500.
    """

    user_id = get_header_user_id(request)

    validate_file_size(session, user_id, file)

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

    # TODO: check if file already exists in DB once we have files per agents

    # Handle uploading File
    try:
        content = await get_file_content(file)
        cleaned_content = content.replace("\x00", "")
        filename = file.filename.encode("ascii", "ignore").decode("utf-8")

        # Create File
        upload_file = FileModel(
            user_id=conversation.user_id,
            conversation_id=conversation.id,
            file_name=filename,
            file_path=filename,
            file_size=file.size,
            file_content=cleaned_content,
        )

        upload_file = file_crud.create_file(session, upload_file)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file {file.filename}."
        )

    return upload_file


@router.post("/batch_upload_file", response_model=list[UploadFileResponse])
async def batch_upload_file(
    session: DBSessionDep,
    request: Request,
    conversation_id: str = Form(None),
    files: list[FastAPIUploadFile] = RequestFile(...),
) -> UploadFileResponse:
    """
    Uploads and creates a batch of File object.
    If no conversation_id is provided, a new Conversation is created as well.

    Args:
        session (DBSessionDep): Database session.
        file (list[FastAPIUploadFile]): List of files to be uploaded.
        conversation_id (Optional[str]): Conversation ID passed from request query parameter.

    Returns:
        list[UploadFileResponse]: List of uploaded files.

    Raises:
        HTTPException: If the conversation with the given ID is not found. Status code 404.
        HTTPException: If the file wasn't uploaded correctly. Status code 500.
    """

    user_id = get_header_user_id(request)

    validate_batch_file_size(session, user_id, files)

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

    # TODO: check if file already exists in DB once we have files per agents

    # Handle uploading File
    files_to_upload = []
    for file in files:
        content = await get_file_content(file)
        cleaned_content = content.replace("\x00", "")
        filename = file.filename.encode("ascii", "ignore").decode("utf-8")

        # Create File
        upload_file = FileModel(
            user_id=conversation.user_id,
            conversation_id=conversation.id,
            file_name=filename,
            file_path=filename,
            file_size=file.size,
            file_content=cleaned_content,
        )
        files_to_upload.append(upload_file)
    try:
        uploaded_files = file_crud.batch_create_files(session, files_to_upload)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file(s): {e}."
        )

    return uploaded_files


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
    _ = validate_conversation(session, conversation_id, user_id)

    files = file_crud.get_files_by_conversation_id(session, conversation_id, user_id)
    return files


@router.put("/{conversation_id}/files/{file_id}", response_model=FilePublic)
async def update_file(
    conversation_id: str,
    file_id: str,
    new_file: UpdateFileRequest,
    session: DBSessionDep,
    request: Request,
) -> FilePublic:
    """
    Update a file by ID.

    Args:
        conversation_id (str): Conversation ID.
        file_id (str): File ID.
        new_file (UpdateFileRequest): New file data.
        session (DBSessionDep): Database session.

    Returns:
        FilePublic: Updated file.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    _ = validate_conversation(session, conversation_id, user_id)
    file = validate_file(session, file_id, user_id)

    file = file_crud.update_file(session, file, new_file)

    return file


@router.delete("/{conversation_id}/files/{file_id}")
async def delete_file(
    conversation_id: str, file_id: str, session: DBSessionDep, request: Request
) -> DeleteFileResponse:
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
    _ = validate_conversation(session, conversation_id, user_id)
    _ = validate_file(session, file_id, user_id)

    file_crud.delete_file(session, file_id, user_id)

    return DeleteFileResponse()


# MISC
@router.post("/{conversation_id}/generate-title", response_model=GenerateTitleResponse)
async def generate_title(
    conversation_id: str, session: DBSessionDep, request: Request
) -> GenerateTitleResponse:
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
    conversation = validate_conversation(session, conversation_id, user_id)

    agent_id = conversation.agent_id if conversation.agent_id else None
    trace_id = request.state.trace_id if hasattr(request.state, "trace_id") else None
    deployment_name = request.headers.get("Deployment-Name", "")
    model_config = get_deployment_config(request)

    title = await generate_conversation_title(
        session,
        conversation,
        deployment_name,
        model_config,
        trace_id,
        user_id,
        agent_id,
    )

    conversation_crud.update_conversation(
        session, conversation, UpdateConversationRequest(title=title)
    )

    return GenerateTitleResponse(title=title)
