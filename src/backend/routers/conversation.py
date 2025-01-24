from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi import File as RequestFile
from fastapi import UploadFile as FastAPIUploadFile
from starlette.responses import Response

from backend.chat.custom.utils import get_deployment
from backend.config.routers import RouterName
from backend.crud import agent as agent_crud
from backend.crud import conversation as conversation_crud
from backend.crud import message as message_crud
from backend.database_models import Conversation as ConversationModel
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import Agent
from backend.schemas.context import Context
from backend.schemas.conversation import (
    ConversationPublic,
    ConversationWithoutMessages,
    DeleteConversationResponse,
    GenerateTitleResponse,
    ToggleConversationPinRequest,
    UpdateConversationRequest,
)
from backend.schemas.file import (
    DeleteConversationFileResponse,
    FileMetadata,
    ListConversationFile,
    UploadConversationFileResponse,
)
from backend.schemas.params.agent import AgentIdQueryParam
from backend.schemas.params.conversation import ConversationIdPathParam, QueryQueryParam
from backend.schemas.params.file import FileIdPathParam
from backend.schemas.params.message import MessageIdPathParam
from backend.schemas.params.model import ModelQueryParam
from backend.schemas.params.shared import OrderByQueryParam, PaginationQueryParams
from backend.services.agent import validate_agent_exists
from backend.services.context import get_context
from backend.services.conversation import (
    filter_conversations,
    generate_conversation_title,
    get_documents_to_rerank,
    get_messages_with_files,
    validate_conversation,
)
from backend.services.file import (
    attach_conversation_id_to_files,
    get_file_service,
    validate_file,
)
from backend.services.synthesizer import synthesize

router = APIRouter(
    prefix="/v1/conversations",
    tags=[RouterName.CONVERSATION],
)
router.name = RouterName.CONVERSATION


# CONVERSATIONS
@router.get("/{conversation_id}", response_model=ConversationPublic)
async def get_conversation(
    conversation_id: ConversationIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> ConversationPublic:
    """
    Get a conversation by ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    conversation = conversation_crud.get_conversation(
        session, conversation_id, user_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

    files = get_file_service().get_files_by_conversation_id(
        session, user_id, conversation.id, ctx
    )
    files_with_conversation_id = attach_conversation_id_to_files(
        conversation.id, files)
    messages = get_messages_with_files(
        session, user_id, conversation.messages, ctx)
    _ = validate_conversation(session, conversation_id, user_id)

    conversation = ConversationPublic(
        id=conversation.id,
        user_id=user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        title=conversation.title,
        messages=messages,
        files=files_with_conversation_id,
        description=conversation.description,
        agent_id=conversation.agent_id,
        organization_id=conversation.organization_id,
        is_pinned=conversation.is_pinned,
    )

    _ = validate_conversation(session, conversation_id, user_id)
    return conversation


@router.get("", response_model=list[ConversationWithoutMessages])
async def list_conversations(
    *,
    page_params: PaginationQueryParams,
    order_by: OrderByQueryParam = None,
    agent_id: AgentIdQueryParam = None,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[ConversationWithoutMessages]:
    """
    List all conversations.
    """
    user_id = ctx.get_user_id()

    conversations = conversation_crud.get_conversations(
        session, offset=page_params.offset, limit=page_params.limit, order_by=order_by, user_id=user_id, agent_id=agent_id
    )

    results = []
    for conversation in conversations:
        files = get_file_service().get_files_by_conversation_id(
            session, user_id, conversation.id, ctx
        )
        files_with_conversation_id = attach_conversation_id_to_files(
            conversation.id, files
        )
        results.append(
            ConversationWithoutMessages(
                id=conversation.id,
                user_id=user_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                title=conversation.title,
                files=files_with_conversation_id,
                description=conversation.description,
                agent_id=conversation.agent_id,
                messages=[],
                organization_id=conversation.organization_id,
                is_pinned=conversation.is_pinned,
            )
        )

    return results


@router.put("/{conversation_id}", response_model=ConversationPublic)
async def update_conversation(
    conversation_id: ConversationIdPathParam,
    new_conversation: UpdateConversationRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> ConversationPublic:
    """
    Update a conversation by ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    conversation = validate_conversation(session, conversation_id, user_id)
    conversation = conversation_crud.update_conversation(
        session, conversation, new_conversation
    )

    files = get_file_service().get_files_by_conversation_id(
        session, user_id, conversation.id, ctx
    )
    messages = get_messages_with_files(
        session, user_id, conversation.messages, ctx)
    files_with_conversation_id = attach_conversation_id_to_files(
        conversation.id, files)
    return ConversationPublic(
        id=conversation.id,
        user_id=user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        title=conversation.title,
        messages=messages,
        files=files_with_conversation_id,
        description=conversation.description,
        agent_id=conversation.agent_id,
        organization_id=conversation.organization_id,
        is_pinned=conversation.is_pinned,
    )


@router.put("/{conversation_id}/toggle-pin", response_model=ConversationWithoutMessages)
async def toggle_conversation_pin(
    conversation_id: ConversationIdPathParam,
    new_conversation_pin: ToggleConversationPinRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> ConversationWithoutMessages:
    """
    Toggle whether a conversation is pinned or not
    """
    user_id = ctx.get_user_id()
    conversation = validate_conversation(session, conversation_id, user_id)
    conversation = conversation_crud.toggle_conversation_pin(
        session, conversation, new_conversation_pin
    )
    files = get_file_service().get_files_by_conversation_id(
        session, user_id, conversation.id, ctx
    )
    files_with_conversation_id = attach_conversation_id_to_files(
        conversation.id, files
    )
    return ConversationWithoutMessages(
        id=conversation.id,
        user_id=user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        title=conversation.title,
        files=files_with_conversation_id,
        description=conversation.description,
        agent_id=conversation.agent_id,
        messages=[],
        organization_id=conversation.organization_id,
        is_pinned=conversation.is_pinned,
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: ConversationIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteConversationResponse:
    """
    Delete a conversation by ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    conversation = validate_conversation(session, conversation_id, user_id)

    get_file_service().delete_all_conversation_files(
        session, conversation.id, conversation.file_ids, user_id, ctx
    )
    conversation_crud.delete_conversation(session, conversation_id, user_id)

    return DeleteConversationResponse()


@router.get(":search", response_model=list[ConversationWithoutMessages])
async def search_conversations(
    *,
    query: QueryQueryParam,
    page_params: PaginationQueryParams,
    order_by: OrderByQueryParam = None,
    agent_id: AgentIdQueryParam = None,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[ConversationWithoutMessages]:
    """
    Search conversations by title.
    """
    user_id = ctx.get_user_id()
    deployment_name = ctx.get_deployment_name()
    model_deployment = get_deployment(deployment_name, session, ctx)

    agent = None
    if agent_id:
        agent = validate_agent_exists(session, agent_id, user_id)

    if agent_id:
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)

    conversations = conversation_crud.get_conversations(
        session, offset=page_params.offset, limit=page_params.limit, order_by=order_by, user_id=user_id, agent_id=agent_id
    )

    if not conversations:
        return []

    rerank_documents = get_documents_to_rerank(conversations)
    filtered_documents = await filter_conversations(
        query,
        conversations,
        rerank_documents,
        model_deployment,
        ctx,
    )

    results = []
    for conversation in filtered_documents:
        files = get_file_service().get_files_by_conversation_id(
            session, user_id, conversation.id, ctx
        )
        files_with_conversation_id = attach_conversation_id_to_files(
            conversation.id, files
        )
        results.append(
            ConversationWithoutMessages(
                id=conversation.id,
                user_id=user_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                title=conversation.title,
                files=files_with_conversation_id,
                description=conversation.description,
                agent_id=conversation.agent_id,
                messages=[],
                organization_id=conversation.organization_id,
                is_pinned=conversation.is_pinned,
            )
        )
    return results


# FILES
@router.post("/batch_upload_file", response_model=list[UploadConversationFileResponse])
async def batch_upload_file(
    *,
    conversation_id: str = Form(None),
    files: list[FastAPIUploadFile] = RequestFile(...),
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> UploadConversationFileResponse:
    """
    Uploads and creates a batch of File object.
    If no conversation_id is provided, a new Conversation is created as well.

    Raises:
        HTTPException: If the conversation with the given ID is not found. Status code 404.
        HTTPException: If the file wasn't uploaded correctly. Status code 500.
    """

    user_id = ctx.get_user_id()

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
                    detail="user_id is required if no valid conversation is provided.",
                )

            # Create new conversation
            conversation = conversation_crud.create_conversation(
                session,
                ConversationModel(user_id=user_id),
            )

    # TODO: check if file already exists in DB once we have files per agents

    try:
        uploaded_files = await get_file_service().create_conversation_files(
            session,
            files,
            user_id,
            conversation.id,
            ctx,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while uploading file(s): {e}."
        )

    files_with_conversation_id = attach_conversation_id_to_files(
        conversation.id, uploaded_files
    )
    return files_with_conversation_id


@router.get("/{conversation_id}/files", response_model=list[ListConversationFile])
async def list_files(
    conversation_id: ConversationIdPathParam,
    session: DBSessionDep, ctx:
    Context = Depends(get_context),
) -> list[ListConversationFile]:
    """
    List all files from a conversation. Important - no pagination support yet.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    _ = validate_conversation(session, conversation_id, user_id)

    files = get_file_service().get_files_by_conversation_id(
        session, user_id, conversation_id, ctx
    )
    files_with_conversation_id = attach_conversation_id_to_files(
        conversation_id, files)
    return files_with_conversation_id


@router.get("/{conversation_id}/files/{file_id}", response_model=FileMetadata)
async def get_file(
    conversation_id: ConversationIdPathParam,
    file_id: FileIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> FileMetadata:
    """
    Get a conversation file by ID.

    Raises:
        HTTPException: If the conversation or file with the given ID is not found, or if the file does not belong to the conversation.
    """
    user_id = ctx.get_user_id()

    conversation = validate_conversation(session, conversation_id, user_id)

    if file_id not in conversation.file_ids:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} does not belong to the conversation with ID: {conversation.id}."
        )

    file = validate_file(session, file_id, user_id)

    return FileMetadata(
        id=file.id,
        file_name=file.file_name,
        file_content=file.file_content,
        file_size=file.file_size,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )


@router.delete("/{conversation_id}/files/{file_id}")
async def delete_file(
    conversation_id: ConversationIdPathParam,
    file_id: FileIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteConversationFileResponse:
    """
    Delete a file by ID.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    _ = validate_conversation(session, conversation_id, user_id)
    validate_file(session, file_id, user_id)
    # Delete the File DB object
    get_file_service().delete_conversation_file_by_id(
        session, conversation_id, file_id, user_id, ctx
    )

    return DeleteConversationFileResponse()


# MISC
@router.post("/{conversation_id}/generate-title", response_model=GenerateTitleResponse)
async def generate_title(
    *,
    conversation_id: ConversationIdPathParam,
    model: ModelQueryParam = "command-r",
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> GenerateTitleResponse:
    """
    Generate a title for a conversation and update the conversation with the generated title.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    ctx.with_deployment_config()
    ctx.with_model(model)

    conversation = validate_conversation(session, conversation_id, user_id)
    agent_id = conversation.agent_id if conversation.agent_id else None

    if agent_id:
        agent = agent_crud.get_agent_by_id(session, agent_id, user_id)
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)

    title, error = await generate_conversation_title(
        session,
        conversation,
        agent_id,
        ctx,
        model,
    )

    conversation_crud.update_conversation(
        session, conversation, UpdateConversationRequest(title=title)
    )

    return GenerateTitleResponse(
        title=title,
        error=error,
    )


# SYNTHESIZE
@router.get("/{conversation_id}/synthesize/{message_id}")
async def synthesize_message(
    conversation_id: ConversationIdPathParam,
    message_id: MessageIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Response:
    """
    Generate a synthesized audio for a specific message in a conversation.

    Raises:
        HTTPException: If the message with the given ID is not found or synthesis fails.
    """
    user_id = ctx.get_user_id()
    message = message_crud.get_conversation_message(session, conversation_id, message_id, user_id)

    if not message:
        raise HTTPException(
            status_code=404,
            detail=f"Message with ID: {message_id} not found.",
        )

    try:
        synthesized_audio = synthesize(message.text)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while message synthesis: {e}"
        )

    return Response(synthesized_audio, media_type="audio/mp3")
