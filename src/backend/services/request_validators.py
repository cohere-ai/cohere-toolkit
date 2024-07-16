from urllib.parse import unquote_plus

from fastapi import HTTPException, Request

import backend.crud.user as user_crud
from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.crud import conversation as conversation_crud
from backend.database_models.database import DBSessionDep
from backend.services.auth.utils import get_header_user_id


def validate_user_header(session: DBSessionDep, request: Request):
    """
    Validate that the request has the `User-Id` header, used for requests
    that require a User.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If no `User-Id` header.

    """

    user_id = request.headers.get("User-Id")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="User-Id required in request headers."
        )

    user = user_crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")


def validate_deployment_header(request: Request):
    """
    Validate that the request has the `Deployment-Name` header, used for chat requests
    that require a deployment (e.g: Cohere Platform, SageMaker).

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If no `Deployment-Name` header.

    """
    deployment_name = request.headers.get("Deployment-Name")
    if deployment_name and not deployment_name in AVAILABLE_MODEL_DEPLOYMENTS.keys():
        raise HTTPException(
            status_code=404,
            detail=f"Deployment {deployment_name} was not found, or is not available.",
        )


async def validate_chat_request(session: DBSessionDep, request: Request):
    """
    Validate that the request has the appropriate values in the body

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    # Validate that the agent_id is valid
    body = await request.json()
    user_id = request.headers.get("User-Id")

    agent_id = request.query_params.get("agent_id")
    if agent_id:
        agent = agent_crud.get_agent_by_id(session, agent_id)
        if agent is None:
            raise HTTPException(
                status_code=400, detail=f"Agent with ID {agent_id} not found."
            )

    # If conversation_id is passed in with agent_id, then make sure that conversation exists with the agent_id
    conversation_id = body.get("conversation_id")
    if conversation_id and agent_id:
        conversation = conversation_crud.get_conversation(
            session, conversation_id, user_id
        )
        if conversation is None or conversation.agent_id != agent_id:
            raise HTTPException(
                status_code=400,
                detail=f"Conversation ID {conversation_id} not found for specified agent.",
            )

    tools = body.get("tools")
    if not tools:
        return

    managed_tools = [tool["name"] for tool in tools if tool["name"] in AVAILABLE_TOOLS]
    if len(managed_tools) > 0 and len(tools) != len(managed_tools):
        raise HTTPException(
            status_code=400, detail="Cannot mix both managed and custom tools"
        )

    if len(managed_tools) == 0:
        for tool in tools:
            if not tool.get("description"):
                raise HTTPException(
                    status_code=400, detail="Custom tools must have a description"
                )


async def validate_env_vars(request: Request):
    """
    Validate that the request has valid env vars.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the header

    """
    body = await request.json()
    env_vars = body.get("env_vars")
    invalid_keys = []

    name = unquote_plus(request.path_params.get("name"))

    if not (deployment := AVAILABLE_MODEL_DEPLOYMENTS.get(name)):
        raise HTTPException(
            status_code=404,
            detail="Deployment not found",
        )

    for key in env_vars:
        if key not in deployment.env_vars:
            invalid_keys.append(key)

    if invalid_keys:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Environment variables not valid for deployment: "
                + ",".join(invalid_keys)
            ),
        )


async def validate_create_agent_request(session: DBSessionDep, request: Request):
    """
    Validate that the create agent request has valid tools, deployments, and compatible models.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    body = await request.json()

    # TODO @scott-cohere: for now we disregard versions and assume agents have unique names, enforce versioning later
    agent_name = body.get("name")
    agent = agent_crud.get_agent_by_name(session, agent_name)
    if agent:
        raise HTTPException(
            status_code=400, detail=f"Agent {agent_name} already exists."
        )

    # Validate tools
    tools = body.get("tools")
    if tools:
        for tool in tools:
            if tool not in AVAILABLE_TOOLS:
                raise HTTPException(status_code=400, detail=f"Tool {tool} not found.")

    name = body.get("name")
    model = body.get("model")
    deployment = body.get("deployment")
    if not name or not model or not deployment:
        raise HTTPException(
            status_code=400, detail="Name, model, and deployment are required."
        )

    # Validate deployment
    if deployment not in AVAILABLE_MODEL_DEPLOYMENTS.keys():
        raise HTTPException(
            status_code=400,
            detail=f"Deployment {deployment} not found or is not available.",
        )

    # Validate model
    if model not in AVAILABLE_MODEL_DEPLOYMENTS[deployment].models:
        raise HTTPException(
            status_code=400,
            detail=f"Model {model} not found for deployment {deployment}.",
        )


async def validate_update_agent_request(session: DBSessionDep, request: Request):
    """
    Validate that the update agent request has valid tools, deployments, and compatible models.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    agent_id = request.path_params.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID is required.")

    agent = agent_crud.get_agent_by_id(session, agent_id)
    if not agent:
        raise HTTPException(
            status_code=400, detail=f"Agent with ID {agent_id} not found."
        )

    if agent.user_id != get_header_user_id(request):
        raise HTTPException(
            status_code=401, detail=f"Agent with ID {agent_id} does not belong to user."
        )

    body = await request.json()
    # Validate tools
    tools = body.get("tools")
    if tools:
        for tool in tools:
            if tool not in AVAILABLE_TOOLS:
                raise HTTPException(status_code=400, detail=f"Tool {tool} not found.")

    model, deployment = body.get("model"), body.get("deployment")
    # Model and deployment must be updated together to ensure compatibility
    if not model and deployment:
        raise HTTPException(
            status_code=400,
            detail="If updating an agent's deployment type, the model must also be provided.",
        )
    elif model and not deployment:
        raise HTTPException(
            status_code=400,
            detail=f"If updating an agent's model, the deployment must also be provided.",
        )
    elif model and deployment:
        # Validate deployment
        if deployment not in AVAILABLE_MODEL_DEPLOYMENTS.keys():
            raise HTTPException(
                status_code=400,
                detail=f"Deployment {deployment} not found or is not available.",
            )

        # Validate model
        if model not in AVAILABLE_MODEL_DEPLOYMENTS[deployment].models:
            raise HTTPException(
                status_code=400,
                detail=f"Model {model} not found for deployment {deployment}.",
            )
