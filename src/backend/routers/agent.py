import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi import File as RequestFile
from fastapi import UploadFile as FastAPIUploadFile

from backend.config.auth import is_authentication_enabled
from backend.config.default_agent import DEFAULT_AGENT_ID, get_default_agent
from backend.config.routers import RouterName
from backend.crud import agent as agent_crud
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.crud import file as file_crud
from backend.crud import snapshot as snapshot_crud
from backend.database_models.agent import Agent as AgentModel
from backend.database_models.agent_tool_metadata import (
    AgentToolMetadata as AgentToolMetadataModel,
)
from backend.database_models.database import DBSessionDep
from backend.routers.utils import (
    get_default_deployment_model,
    get_deployment_model_from_agent,
)
from backend.schemas.agent import (
    Agent,
    AgentPublic,
    AgentToolMetadata,
    AgentToolMetadataPublic,
    AgentVisibility,
    CreateAgentRequest,
    CreateAgentToolMetadataRequest,
    DeleteAgent,
    DeleteAgentToolMetadata,
    UpdateAgentDB,
    UpdateAgentRequest,
    UpdateAgentToolMetadataRequest,
)
from backend.schemas.context import Context
from backend.schemas.deployment import DeploymentDefinition
from backend.schemas.file import (
    DeleteAgentFileResponse,
    FileMetadata,
    UploadAgentFileResponse,
)
from backend.schemas.params.agent import (
    AgentIdPathParam,
    AgentToolMetadataIdPathParam,
    VisibilityQueryParam,
)
from backend.schemas.params.file import FileIdPathParam
from backend.schemas.params.organization import OrganizationIdQueryParam
from backend.schemas.params.shared import PaginationQueryParams
from backend.services.agent import (
    raise_db_error,
    validate_agent_exists,
    validate_agent_tool_metadata_exists,
)
from backend.services.context import get_context
from backend.services.file import (
    get_file_service,
    validate_file,
)
from backend.services.request_validators import (
    validate_create_agent_request,
    validate_update_agent_request,
    validate_user_header,
)

router = APIRouter(
    prefix="/v1/agents",
    tags=[RouterName.AGENT],
)
router.name = RouterName.AGENT

auth_dependencies = [] if is_authentication_enabled() else [Depends(validate_user_header)]


@router.post(
    "",
    response_model=AgentPublic,
    dependencies=[
        *auth_dependencies,
        Depends(validate_create_agent_request),
    ],
)
async def create_agent(
    agent: CreateAgentRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> AgentPublic:
    """
    Create an agent.

    Raises:
        HTTPException: If the agent creation fails.
    """
    ctx.with_user(session)
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()
    logger.debug(event="Creating agent", user_id=user_id, agent=agent.model_dump())

    deployment_db, model_db = get_deployment_model_from_agent(agent, session)
    default_deployment_db, default_model_db = get_default_deployment_model(session)
    logger.debug(event="Deployment and model", deployment=deployment_db, model=model_db)

    if not deployment_db or not model_db:
        logger.error(event="Unable to find deployment or model, using defaults", agent=agent)

        if not default_deployment_db or not default_model_db:
            logger.error(event="Unable to find default deployment or model", agent=agent)
            raise HTTPException(status_code=400, detail="Unable to find deployment or model")

        deployment_db = default_deployment_db
        model_db = default_model_db

    try:
        agent_data = AgentModel(
            name=agent.name,
            description=agent.description,
            preamble=agent.preamble,
            temperature=agent.temperature,
            user_id=user_id,
            organization_id=agent.organization_id,
            tools=agent.tools,
            is_private=agent.is_private,
            deployment_id=deployment_db.id,
            model_id=model_db.id,
        )

        created_agent = agent_crud.create_agent(session, agent_data)

        if not created_agent:
            raise HTTPException(status_code=500, detail="Failed to create Agent")

        if agent.tools_metadata:
            for tool_metadata in agent.tools_metadata:
                await update_or_create_tool_metadata(
                    created_agent, tool_metadata, session, ctx
                )

        agent_schema = Agent.model_validate(created_agent)
        ctx.with_agent(agent_schema)
        logger.debug(event="Agent created", agent=created_agent)
        return created_agent
    except Exception as e:
        logger.exception(event=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[AgentPublic])
async def list_agents(
    *,
    page_params: PaginationQueryParams,
    visibility: VisibilityQueryParam = AgentVisibility.ALL,
    org_id: OrganizationIdQueryParam = None,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[AgentPublic]:
    """
    List all agents.
    """
    logger = ctx.get_logger()
    # TODO: get organization_id from user
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()
    # request organization_id is used for filtering agents instead of header Organization-Id if enabled
    if org_id:
        logger.debug(event="Request limited to organization", organization_id=org_id)
        ctx.without_global_filtering()

    try:
        agents = agent_crud.get_agents(
            session,
            user_id=user_id,
            offset=page_params.offset,
            limit=page_params.limit,
            visibility=visibility,
            organization_id=org_id,
        )
        # Tradeoff: This appends the default Agent regardless of pagination
        agents.append(get_default_agent())
        logger.debug(event="Returning agents:", agents=agents)
        return agents
    except Exception as e:
        logger.exception(event=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent_by_id(
    agent_id: AgentIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context)
) -> AgentPublic:
    """
    Return an agent by ID.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    agent = None

    try:
        # Intentionally not adding Default Agent to DB so it's more flexible
        if agent_id == DEFAULT_AGENT_ID:
            agent = get_default_agent()
        else:
            agent = agent_crud.get_agent_by_id(session, agent_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent with ID {agent_id} not found.",
        )

    agent_schema = Agent.model_validate(agent)
    ctx.with_agent(agent_schema)
    return agent


@router.get("/{agent_id}/deployments", response_model=list[DeploymentDefinition])
async def get_agent_deployment(
    agent_id: AgentIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context)
) -> list[DeploymentDefinition]:
    """
    Get the deployment for an agent

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    agent = validate_agent_exists(session, agent_id, user_id)

    agent_schema = Agent.model_validate(agent)
    ctx.with_agent(agent_schema)

    return [
        DeploymentDefinition.from_db_deployment(deployment)
        for deployment in agent.deployments
    ]


@router.put(
    "/{agent_id}",
    response_model=AgentPublic,
    dependencies=[
        *auth_dependencies,
        Depends(validate_update_agent_request),
    ],
)
async def update_agent(
    agent_id: AgentIdPathParam,
    new_agent: UpdateAgentRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> AgentPublic:
    """
    Update an agent by ID.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    ctx.with_user(session)
    agent = validate_agent_exists(session, agent_id, user_id)

    if new_agent.tools_metadata is not None:
        agent = await handle_tool_metadata_update(agent, new_agent, session, ctx)

    # If the agent was public and is now private, we need to delete all snapshots associated with it
    snapshot_deletion_task = None
    if not agent.is_private and new_agent.is_private:
        snapshot_deletion_task = asyncio.create_task(
            snapshot_crud.delete_snapshots_by_agent_id(session, agent_id)
        )

    try:
        db_deployment, db_model = get_deployment_model_from_agent(new_agent, session)
        new_agent_db = UpdateAgentDB(**new_agent.model_dump())
        if db_deployment and db_model:
            new_agent_db.model_id = db_model.id
            new_agent_db.deployment_id = db_deployment.id
        agent = agent_crud.update_agent(
            session, agent, new_agent_db, user_id
        )
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Wait for snapshot deletion task to finish
        if snapshot_deletion_task:
            await snapshot_deletion_task

    return agent


@router.delete("/{agent_id}", response_model=DeleteAgent)
async def delete_agent(
    agent_id: AgentIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteAgent:
    """
    Delete an agent by ID.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    agent = validate_agent_exists(session, agent_id, user_id)
    agent_schema = Agent.model_validate(agent)
    ctx.with_agent(agent_schema)

    deleted = agent_crud.delete_agent(session, agent_id, user_id)
    if not deleted:
        raise HTTPException(status_code=401, detail="Could not delete Agent.")

    return DeleteAgent()


# Agent Tool Metadata endpoints


async def handle_tool_metadata_update(
    agent: Agent,
    new_agent: Agent,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Agent:
    """Update or create tool metadata for an agent.

    Args:
        agent (Agent): Agent.
        new_agent (Agent): New agent data.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        Agent: Agent.
    """
    user_id = ctx.get_user_id()
    validate_agent_exists(session, agent.id, user_id)

    # Delete tool metadata that are not in the request
    new_tools_names = [metadata.tool_name for metadata in new_agent.tools_metadata]
    for tool_metadata in agent.tools_metadata:
        if tool_metadata.tool_name not in new_tools_names:
            agent_tool_metadata_crud.delete_agent_tool_metadata_by_id(
                session, tool_metadata.id
            )

    # Create or update tool metadata from the request
    for tool_metadata in new_agent.tools_metadata:
        try:
            await update_or_create_tool_metadata(agent, tool_metadata, session, ctx)
        except Exception as e:
            raise_db_error(e, "Tool name", tool_metadata.tool_name)

    # Remove tools_metadata from new_agent to avoid updating it in the agent
    new_agent.tools_metadata = None
    agent = agent_crud.get_agent_by_id(session, agent.id, user_id)
    return agent


async def update_or_create_tool_metadata(
    agent: Agent,
    new_tool_metadata: AgentToolMetadata,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> None:
    """Update or create tool metadata for an agent.

    Args:
        agent (Agent): Agent.
        new_tool_metadata (AgentToolMetadata): New tool metadata.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.
    """

    existing_tools_names = [metadata.tool_name for metadata in agent.tools_metadata]
    if new_tool_metadata.tool_name in existing_tools_names or new_tool_metadata.id:
        await update_agent_tool_metadata(
            agent.id, new_tool_metadata.id, new_tool_metadata, session, ctx
        )
    else:
        create_metadata_req = CreateAgentToolMetadataRequest(
            **new_tool_metadata.model_dump(exclude_none=True)
        )
        create_agent_tool_metadata(agent.id, create_metadata_req, session, ctx)


@router.get("/{agent_id}/tool-metadata", response_model=list[AgentToolMetadataPublic])
async def list_agent_tool_metadata(
    agent_id: AgentIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context)
) -> list[AgentToolMetadataPublic]:
    """
    List all agent tool metadata by agent ID.

    Raises:
        HTTPException: If the agent tool metadata retrieval fails.
    """
    user_id = ctx.get_user_id()
    validate_agent_exists(session, agent_id, user_id)

    try:
        return agent_tool_metadata_crud.get_all_agent_tool_metadata_by_agent_id(
            session, agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{agent_id}/tool-metadata",
    response_model=AgentToolMetadataPublic,
)
def create_agent_tool_metadata(
    agent_id: AgentIdPathParam,
    agent_tool_metadata: CreateAgentToolMetadataRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> AgentToolMetadataPublic:
    """
    Create an agent tool metadata.

    Raises:
        HTTPException: If the agent tool metadata creation fails.
    """
    user_id = ctx.get_user_id()
    agent = validate_agent_exists(session, agent_id, user_id)
    agent_schema = Agent.model_validate(agent)
    ctx.with_agent(agent_schema)

    agent_tool_metadata_data = AgentToolMetadataModel(
        user_id=user_id,
        agent_id=agent_id,
        tool_name=agent_tool_metadata.tool_name,
        artifacts=agent_tool_metadata.artifacts,
    )

    try:
        created_agent_tool_metadata = (
            agent_tool_metadata_crud.create_agent_tool_metadata(
                session, agent_tool_metadata_data
            )
        )

        metadata_schema = AgentToolMetadata.model_validate(created_agent_tool_metadata)
        ctx.with_agent_tool_metadata(metadata_schema)
    except Exception as e:
        raise_db_error(e, "Tool name", agent_tool_metadata.tool_name)

    return created_agent_tool_metadata


@router.put("/{agent_id}/tool-metadata/{agent_tool_metadata_id}")
async def update_agent_tool_metadata(
    agent_id: AgentIdPathParam,
    agent_tool_metadata_id: AgentToolMetadataIdPathParam,
    new_agent_tool_metadata: UpdateAgentToolMetadataRequest,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> AgentToolMetadata:
    """
    Update an agent tool metadata by ID.

    Raises:
        HTTPException: If the agent tool metadata with the given ID is not found.
        HTTPException: If the agent tool metadata update fails.
    """
    user_id = ctx.get_user_id()
    validate_agent_exists(session, agent_id, user_id)

    agent_tool_metadata = validate_agent_tool_metadata_exists(
        session, agent_tool_metadata_id
    )

    try:
        agent_tool_metadata_crud.update_agent_tool_metadata(
            session, agent_tool_metadata, new_agent_tool_metadata
        )
        metadata_schema = AgentToolMetadata.model_validate(agent_tool_metadata)
        ctx.with_agent_tool_metadata(metadata_schema)
    except Exception as e:
        raise_db_error(e, "Tool name", agent_tool_metadata.tool_name)

    return agent_tool_metadata


@router.delete("/{agent_id}/tool-metadata/{agent_tool_metadata_id}")
async def delete_agent_tool_metadata(
    agent_id: AgentIdPathParam,
    agent_tool_metadata_id: AgentToolMetadataIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteAgentToolMetadata:
    """
    Delete an agent tool metadata by ID.

    Raises:
        HTTPException: If the agent tool metadata with the given ID is not found.
        HTTPException: If the agent tool metadata deletion fails.
    """
    user_id = ctx.get_user_id()
    validate_agent_exists(session, agent_id, user_id)

    agent_tool_metadata = validate_agent_tool_metadata_exists(
        session, agent_tool_metadata_id
    )

    metadata_schema = AgentToolMetadata.model_validate(agent_tool_metadata)
    ctx.with_agent_tool_metadata(metadata_schema)
    try:
        agent_tool_metadata_crud.delete_agent_tool_metadata_by_id(
            session, agent_tool_metadata_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return DeleteAgentToolMetadata()


@router.post("/batch_upload_file", response_model=list[UploadAgentFileResponse])
async def batch_upload_file(
    *,
    files: list[FastAPIUploadFile] = RequestFile(...),
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> UploadAgentFileResponse:
    """
    Upload a batch of files
    """
    user_id = ctx.get_user_id()

    uploaded_files = []
    try:
        uploaded_files = await get_file_service().create_agent_files(
            session,
            files,
            user_id,
            ctx,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while uploading agent file(s): {e}."
        )

    return uploaded_files


@router.get("/{agent_id}/files/{file_id}", response_model=FileMetadata)
async def get_agent_file(
    agent_id: AgentIdPathParam,
    file_id: FileIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> FileMetadata:
    """
    Get an agent file by ID.

    Raises:
        HTTPException: If the agent or file with the given ID is not found, or if the file does not belong to the agent.
    """
    user_id = ctx.get_user_id()

    if file_id not in get_file_service().get_file_ids_by_agent_id(session, user_id, agent_id, ctx):
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} does not belong to the agent with ID: {agent_id}."
        )

    file = file_crud.get_file(session, file_id)

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} not found.",
        )

    return FileMetadata(
        id=file.id,
        file_name=file.file_name,
        file_content=file.file_content,
        file_size=file.file_size,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )


@router.delete("/{agent_id}/files/{file_id}")
async def delete_agent_file(
    agent_id: AgentIdPathParam,
    file_id: FileIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteAgentFileResponse:
    """
    Delete an agent file by ID.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    _ = validate_agent_exists(session, agent_id, user_id)
    validate_file(session, file_id, user_id)

    # Delete the File DB object
    get_file_service().delete_agent_file_by_id(session, agent_id, file_id, user_id, ctx)

    return DeleteAgentFileResponse()
