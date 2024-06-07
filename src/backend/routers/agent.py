from fastapi import APIRouter, Depends
from fastapi import Form, HTTPException, Request

from backend.config.routers import RouterName
from backend.database_models.agent import Agent
from backend.database_models.database import DBSessionDep
from backend.services.auth.utils import get_header_user_id
from backend.crud import agent as agent_crud
from backend.services.request_validators import validate_create_agent_request
from backend.schemas.agent import Agent as AgentSchema, UpdateAgent as UpdateAgentSchema, DeleteAgent as DeleteAgentSchema


router = APIRouter(
    prefix="/v1/agents",
)
router.name = RouterName.AGENT

@router.post("/", dependencies=[Depends(validate_create_agent_request)], response_model=AgentSchema)
def create_agent(session: DBSessionDep, request: Request):
  user_id = get_header_user_id(request)

  agent_data = Agent(
    name=request.json().get("name"),
    user_id=user_id,
    version=request.json().get("version"),
    description=request.json().get("description"),
    preamble=request.json().get("preamble"),
    temperature=request.json().get("temperature"),
    model=request.json().get("model"),
    deployment=request.json().get("deployment"),
    # tools=request.json().get("tools"),
  )

  agent = agent_crud.create_agent(session, agent_data)
  return agent


@router.get("", response_model=list[AgentSchema])
async def list_conversations(
    *, offset: int = 0, limit: int = 100, session: DBSessionDep, request: Request
) -> list[AgentSchema]:
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
    user_id = get_header_user_id(request)
    return agent_crud.get_agents(
        session, offset=offset, limit=limit, user_id=user_id
    )


@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(
    agent_id: str, session: DBSessionDep, request: Request
) -> AgentSchema:
    """
    Args:
        conversation_id (str): Conversation ID.
        session (DBSessionDep): Database session.

    Returns:
        list[ListFile]: List of files from the conversation.

    Raises:
        HTTPException: If the conversation with the given ID is not found.
    """
    user_id = get_header_user_id(request)
    agent = agent_crud.get_agent(session, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent with ID: {agent_id} not found.",
        )

    return agent


@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(
    agent_id: str,
    new_agent: UpdateAgentSchema,
    session: DBSessionDep,
    request: Request,
) -> AgentSchema:
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
    agent = agent_crud.update_agent(session, agent_id, user_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent with ID: {agent_id} not found.",
        )

    agent = agent_crud.update_agent(
        session, agent, new_agent
    )

    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str, session: DBSessionDep, request: Request
) -> DeleteAgentSchema:
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
    agent = agent_crud.get_agent(session, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent with ID: {agent_id} not found.",
        )

    agent_crud.delete_agent(session, agent_id)

    return DeleteAgentSchema()
