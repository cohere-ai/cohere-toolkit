import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi import File as RequestFile
from fastapi import UploadFile as FastAPIUploadFile

from backend.config.routers import RouterName
from backend.crud import agent as agent_crud
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
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
from backend.schemas.deployment import Deployment as DeploymentSchema
from backend.schemas.file import DeleteAgentFileResponse, UploadAgentFileResponse
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
)
router.name = RouterName.AGENT


@router.post(
    "",
    response_model=AgentPublic,
    dependencies=[
        Depends(validate_user_header),
        Depends(validate_create_agent_request),
    ],
)
async def create_agent(
        session: DBSessionDep,
        agent: CreateAgentRequest,
        ctx: Context = Depends(get_context),
) -> AgentPublic:
    """
    Create an agent.

    Args:
        session (DBSessionDep): Database session.
        agent (CreateAgentRequest): Agent data.
        ctx (Context): Context object.
    Returns:
        AgentPublic: Created agent with no user ID or organization ID.
    Raises:
        HTTPException: If the agent creation fails.
    """
    ctx.with_user(session)
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()

    deployment_db, model_db = get_deployment_model_from_agent(agent, session)
    default_deployment_db, default_model_db = get_default_deployment_model(session)
    try:
        if deployment_db and model_db:
            agent_data = AgentModel(
                name=agent.name,
                description=agent.description,
                preamble=agent.preamble,
                temperature=agent.temperature,
                user_id=user_id,
                organization_id=agent.organization_id,
                tools=agent.tools,
                is_private=agent.is_private,
                deployment_id=deployment_db.id if deployment_db else default_deployment_db.id if default_deployment_db else None,
                model_id=model_db.id if model_db else default_model_db.id if default_model_db else None,
            )

            created_agent = agent_crud.create_agent(session, agent_data)

            if agent.tools_metadata:
                for tool_metadata in agent.tools_metadata:
                    await update_or_create_tool_metadata(
                        created_agent, tool_metadata, session, ctx
                    )

            agent_schema = Agent.model_validate(created_agent)
            ctx.with_agent(agent_schema)
            return created_agent

    except Exception as e:
        logger.exception(event=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[AgentPublic])
async def list_agents(
        *,
        offset: int = 0,
        limit: int = 100,
        session: DBSessionDep,
        visibility: AgentVisibility = AgentVisibility.ALL,
        organization_id: Optional[str] = None,
        ctx: Context = Depends(get_context),
) -> list[AgentPublic]:
    """
    List all agents.

    Args:
        offset (int): Offset to start the list.
        limit (int): Limit of agents to be listed.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        list[AgentPublic]: List of agents with no user ID or organization ID.
    """
    # TODO: get organization_id from user
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()
    # request organization_id is used for filtering agents instead of header Organization-Id if enabled
    if organization_id:
        ctx.without_global_filtering()

    try:
        agents = agent_crud.get_agents(
            session,
            user_id=user_id,
            offset=offset,
            limit=limit,
            visibility=visibility,
            organization_id=organization_id,
        )
        return agents
    except Exception as e:
        logger.exception(event=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent_by_id(
        agent_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
) -> Agent:
    """
    Args:
        agent_id (str): Agent ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        Agent: Agent.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    agent = None

    try:
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


@router.get("/{agent_id}/deployments", response_model=list[DeploymentSchema])
async def get_agent_deployment(
        agent_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
) -> DeploymentSchema:
    """
    Args:
        agent_id (str): Agent ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        Agent: Agent.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    agent = validate_agent_exists(session, agent_id, user_id)

    agent_schema = Agent.model_validate(agent)
    ctx.with_agent(agent_schema)

    return DeploymentSchema.custom_transform(agent.deployment)


@router.put(
    "/{agent_id}",
    response_model=AgentPublic,
    dependencies=[
        Depends(validate_user_header),
        Depends(validate_update_agent_request),
    ],
)
async def update_agent(
        agent_id: str,
        new_agent: UpdateAgentRequest,
        session: DBSessionDep,
        ctx: Context = Depends(get_context),
) -> AgentPublic:
    """
    Update an agent by ID.

    Args:
        agent_id (str): Agent ID.
        new_agent (UpdateAgentRequest): New agent data.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        AgentPublic: Updated agent with no user ID or organization ID.

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
        new_agent_db = UpdateAgentDB(**new_agent.dict())
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
        agent_id: str,
        session: DBSessionDep,
        ctx: Context = Depends(get_context),
) -> DeleteAgent:
    """
    Delete an agent by ID.

    Args:
        agent_id (str): Agent ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        DeleteAgent: Empty response.

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
        request (Request): Request object.
        ctx (Context): Context object.
    """

    existing_tools_names = [metadata.tool_name for metadata in agent.tools_metadata]
    if new_tool_metadata.tool_name in existing_tools_names or new_tool_metadata.id:
        await update_agent_tool_metadata(
            agent.id, new_tool_metadata.id, session, new_tool_metadata, ctx
        )
    else:
        create_metadata_req = CreateAgentToolMetadataRequest(
            **new_tool_metadata.model_dump(exclude_none=True)
        )
        create_agent_tool_metadata(session, agent.id, create_metadata_req, ctx)


@router.get("/{agent_id}/tool-metadata", response_model=list[AgentToolMetadataPublic])
async def list_agent_tool_metadata(
        agent_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
) -> list[AgentToolMetadataPublic]:
    """
    List all agent tool metadata by agent ID.

    Args:
        agent_id (str): Agent ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        list[AgentToolMetadataPublic]: List of agent tool metadata with no user ID or organization ID.

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
        session: DBSessionDep,
        agent_id: str,
        agent_tool_metadata: CreateAgentToolMetadataRequest,
        ctx: Context = Depends(get_context),
) -> AgentToolMetadataPublic:
    """
    Create an agent tool metadata.

    Args:
        session (DBSessionDep): Database session.
        agent_id (str): Agent ID.
        agent_tool_metadata (CreateAgentToolMetadataRequest): Agent tool metadata data.
        ctx (Context): Context object.

    Returns:
        AgentToolMetadataPublic: Created agent tool metadata.

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
        agent_id: str,
        agent_tool_metadata_id: str,
        session: DBSessionDep,
        new_agent_tool_metadata: UpdateAgentToolMetadataRequest,
        ctx: Context = Depends(get_context),
) -> AgentToolMetadata:
    """
    Update an agent tool metadata by ID.

    Args:
        agent_id (str): Agent ID.
        agent_tool_metadata_id (str): Agent tool metadata ID.
        session (DBSessionDep): Database session.
        new_agent_tool_metadata (UpdateAgentToolMetadataRequest): New agent tool metadata data.
        ctx (Context): Context object.

    Returns:
        AgentToolMetadata: Updated agent tool metadata.

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
        agent_id: str,
        agent_tool_metadata_id: str,
        session: DBSessionDep,
        ctx: Context = Depends(get_context),
) -> DeleteAgentToolMetadata:
    """
    Delete an agent tool metadata by ID.

    Args:
        agent_id (str): Agent ID.
        agent_tool_metadata_id (str): Agent tool metadata ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        DeleteAgentToolMetadata: Empty response.

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
        session: DBSessionDep,
        files: list[FastAPIUploadFile] = RequestFile(...),
        ctx: Context = Depends(get_context),
) -> UploadAgentFileResponse:
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


@router.delete("/{agent_id}/files/{file_id}")
async def delete_agent_file(
        agent_id: str,
        file_id: str,
        session: DBSessionDep,
        ctx: Context = Depends(get_context),
) -> DeleteAgentFileResponse:
    """
    Delete an agent file by ID.

    Args:
        agent_id (str): Agent ID.
        file_id (str): File ID.
        session (DBSessionDep): Database session.

    Returns:
        DeleteFile: Empty response.

    Raises:
        HTTPException: If the agent with the given ID is not found.
    """
    user_id = ctx.get_user_id()
    _ = validate_agent_exists(session, agent_id)
    validate_file(session, file_id, user_id)

    # Delete the File DB object
    get_file_service().delete_agent_file_by_id(session, agent_id, file_id, user_id, ctx)

    return DeleteAgentFileResponse()
