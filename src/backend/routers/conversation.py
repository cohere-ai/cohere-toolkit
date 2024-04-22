from fastapi import APIRouter, Depends
from fastapi import File as RequestFile
from fastapi import Form, HTTPException, Request
from fastapi import UploadFile as FastAPIUploadFile

from backend.crud import conversation as conversation_crud
from backend.crud import file as file_crud
from backend.models import Conversation as ConversationModel
from backend.models import File as FileModel
from backend.models import get_session
from backend.models.database import DBSessionDep
from backend.schemas.conversation import (
    Conversation,
    ConversationWithoutMessages,
    DeleteConversation,
    UpdateConversation,
)
from backend.schemas.file import DeleteFile, File, ListFile, UpdateFile, UploadFile
from backend.services.file.service import FileService
from backend.services.request_validators import validate_user_header

router = APIRouter(
    prefix="/conversations",
    dependencies=[Depends(get_session), Depends(validate_user_header)],
)


# CONVERSATIONS
@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
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
    user_id = request.headers.get("User-Id", "")
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    return conversation


@router.get("/", response_model=list[ConversationWithoutMessages])
def list_conversations(
    *, offset: int = 0, limit: int = 100, session: DBSessionDep, request: Request
) -> list[ConversationWithoutMessages]:
    """
    List all conversations.

    Args:
        offset (int): Offset to start the list.
        limit (int): Limit of conversations to be listed.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        list[ConversationWithoutMessages]: List of conversations.
    """
    user_id = request.headers.get("User-Id")
    return conversation_crud.get_conversations(
        session, offset=offset, limit=limit, user_id=user_id
    )


@router.put("/{conversation_id}", response_model=Conversation)
def update_conversation(
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
    user_id = request.headers.get("User-Id")
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
def delete_conversation(
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
    user_id = request.headers.get("User-Id", "")
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    conversation_crud.delete_conversation(session, conversation_id, user_id)

    return DeleteConversation()


# FILES
@router.post("/{conversation_id}/upload_file", response_model=UploadFile)
async def upload_file_with_conversation(
    conversation_id: str,
    session: DBSessionDep,
    request: Request,
    file: FastAPIUploadFile = RequestFile(...),
) -> UploadFile:
    """
    (TO BE DEPRECATED)


    Uploads a file to a conversation.

    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.
        file (FastAPIUploadFile): File to be uploaded.

    Returns:
        UploadFile: Uploaded file.

    Raises:
        HTTPException: If the conversation with the given ID is not found. Status code 404.
        HTTPException: If the file wasn't uploaded correctly. Status code 500.
    """
    user_id = request.headers.get("User-Id")
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    file_path = FileService().upload_file(file)

    # Raise exception if file wasn't uploaded
    if not file_path.exists():
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file {file.filename}."
        )

    db_file = FileModel(
        user_id=conversation.user_id,
        conversation_id=conversation.id,
        file_name=file_path.name,
        file_path=str(file_path),
        file_size=file_path.stat().st_size,
    )

    db_file = file_crud.create_file(session, db_file)

    return db_file


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

    user_id = request.headers.get("User-Id", "")

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

    # Create File
    upload_file = FileModel(
        user_id=conversation.user_id,
        conversation_id=conversation.id,
        file_name=file_path.name,
        file_path=str(file_path),
        file_size=file_path.stat().st_size,
    )

    upload_file = file_crud.create_file(session, upload_file)

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
    user_id = request.headers.get("User-Id", "")
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
    user_id = request.headers.get("User-Id", "")

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
    user_id = request.headers.get("User-Id", "")
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
