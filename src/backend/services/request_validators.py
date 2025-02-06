from typing import Annotated
from urllib.parse import unquote_plus

from fastapi import Header, HTTPException, Request

import backend.crud.user as user_crud
from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.tools import get_available_tools
from backend.crud import agent as agent_crud
from backend.crud import conversation as conversation_crud
from backend.crud import deployment as deployment_crud
from backend.crud import model as model_crud
from backend.crud import organization as organization_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.deployment import Deployment
from backend.exceptions import DeploymentNotFoundError
from backend.model_deployments.utils import class_name_validator
from backend.services import deployment as deployment_service
from backend.services.agent import validate_agent_exists
from backend.services.auth.utils import get_header_user_id
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


def validate_deployment_model(deployment: str, model: str, session: DBSessionDep):
    """
    Validate that the deployment and model are compatible.

    Args:
        deployment_name (str): The deployment name
        model_name (str): The model name
        session (DBSessionDep): The database session

    Raises:
        HTTPException: If the deployment and model are not compatible

    """
    found = deployment_service.get_deployment_definition_by_name(session, deployment)
    if not found:
        found = deployment_service.get_deployment_definition(session, deployment)
    if not found:
        raise HTTPException(
            status_code=400,
            detail=f"Deployment {deployment} not found or is not available in the Database.",
        )

    deployment_config = next(
        d for d in AVAILABLE_MODEL_DEPLOYMENTS.values() if d.__name__ == found.class_name
    ).to_deployment_definition()
    deployment_model = next(
        (
            model_db
            for model_db in found.models
            if model_db == model
        ),
        None,
    )
    if not deployment_model:
        deployment_model = model_crud.create_model_by_config(
            session, deployment_config, found.id, model
        )
    if not deployment_model:
        raise HTTPException(
            status_code=400,
            detail=f"Model {model} not found for deployment {deployment}.",
        )

    return found, deployment_model


def validate_deployment_config(deployment_config: dict, deployment_db: Deployment) -> None:
    """
    Validate that the deployment config is valid for the deployment.

    Args:
        deployment_config (dict): The deployment config
        deployment_db (Deployment): The deployment database model

    Raises:
        HTTPException: If the deployment config is not valid

    """
    for key in deployment_config:
        if (
            key not in deployment_db.default_deployment_config
            or not deployment_config[key]
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Deployment config key {key} not valid for deployment {deployment_db.name} or is empty.",
            )


def validate_user_header(
    session: DBSessionDep,
    user_id: Annotated[str|None, Header(
        title="User ID",
        description="Unique identifier of User making the request",
    )] = None,
) -> None:
    """
    Validate that the request has the `User-Id` header, used for requests
    that require a User.

    Raises:
        HTTPException: If no `User-Id` header.
    """
    if not user_id:
        logger.error(event="User-Id required in request headers.")
        raise HTTPException(
            status_code=401, detail="User-Id required in request headers."
        )

    user = user_crud.get_user(session, user_id)
    if not user:
        logger.error(event="User not found.", user_id=user_id)
        raise HTTPException(status_code=401, detail="User not found.")


def validate_organization_header(
    session: DBSessionDep,
    Organization_Id: Annotated[str|None, Header( # Not following snake_case so FastAPI parses dependencies properly
        title="Organization ID",
        description="Unique Identifier for the Organization making the request",
    )] = None,
) -> None:
    """
    Validate that the request has the `Organization-Id` header, used for requests
    that require an Organization.

    Raises:
        HTTPException: If no `Organization-Id` header.
    """
    if Organization_Id:
        organization = organization_crud.get_organization(session, Organization_Id)
        if not organization:
            raise HTTPException(status_code=404, detail=f"Organization ID {Organization_Id} not found.")


def validate_deployment_header(
    session: DBSessionDep,
    deployment_name: Annotated[str|None, Header(
        title="Deployment Name",
        description="Name of the Deployment to use for the request",
    )] = None,
) -> None:
    """
    Validate that the request has the `Deployment-Name` header, used for chat requests
    that require a deployment (e.g: Cohere Platform, SageMaker).

    Raises:
        HTTPException: If no `Deployment-Name` header.
    """
    # TODO Eugene: Discuss with Scott
    if deployment_name:
        _ = deployment_service.get_deployment_definition_by_name(session, deployment_name)


async def validate_chat_request(request: Request, session: DBSessionDep):
    """
    Validate that the request has the appropriate values in the body

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    # Validate that the agent_id is valid
    body = await request.json()
    user_id = get_header_user_id(request)

    agent_id = request.query_params.get("agent_id")
    if agent_id:
        validate_agent_exists(session, agent_id, user_id)

    # If conversation_id is passed in with agent_id, then make sure that conversation exists with the agent_id
    conversation_id = body.get("conversation_id")
    if conversation_id and agent_id:
        conversation = conversation_crud.get_conversation(
            session, conversation_id, user_id
        )
        if conversation is None or conversation.agent_id != agent_id:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation ID {conversation_id} not found for specified agent.",
            )

    tools = body.get("tools")
    if not tools:
        return

    managed_tools = [tool["name"] for tool in tools if tool["name"] in get_available_tools()]
    if managed_tools and len(tools) != len(managed_tools):
        raise HTTPException(
            status_code=400, detail="Cannot mix both managed and custom tools"
        )

    if not managed_tools:
        for tool in tools:
            if not tool.get("description"):
                raise HTTPException(
                    status_code=400, detail="Custom tools must have a description"
                )


async def validate_env_vars(session: DBSessionDep, request: Request):
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

    deployment_id = unquote_plus(request.path_params.get("deployment_id", ""))
    try:
        deployment = deployment_service.get_deployment_instance_by_id(session, deployment_id)
    except DeploymentNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Deployment {deployment_id} not found."
        )

    for key in env_vars:
        if key not in deployment.env_vars():
            invalid_keys.append(key)

    if invalid_keys:
        raise HTTPException(
            status_code=400,
            detail=(
                "Environment variables not valid for deployment: "
                + ",".join(invalid_keys)
            ),
        )

    return env_vars


async def validate_create_agent_request(session: DBSessionDep, request: Request):
    """
    Validate that the create agent request has valid tools, deployments, and compatible models.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    user_id = get_header_user_id(request)
    body = await request.json()

    # TODO @scott-cohere: for now we disregard versions and assume agents have unique names, enforce versioning later
    agent_name = body.get("name")
    agent = agent_crud.get_agent_by_name(session, agent_name, user_id=user_id)
    if agent:
        raise HTTPException(
            status_code=400, detail=f"Agent {agent_name} already exists."
        )

    # Validate tools
    tools = body.get("tools")
    if tools:
        for tool in tools:
            if tool not in get_available_tools():
                raise HTTPException(status_code=404, detail=f"Tool {tool} not found.")

    name = body.get("name")
    model = body.get("model")
    deployment = body.get("deployment")
    if not name or not model or not deployment:
        raise HTTPException(
            status_code=400, detail="Name, model, and deployment are required."
        )
    deployment_config = body.get("deployment_config")
    # Validate deployment
    deployment_db, model_db = validate_deployment_model(deployment, model, session)
    if deployment_config:
        validate_deployment_config(deployment_config, deployment_db)


async def validate_update_agent_request(session: DBSessionDep, request: Request):
    """
    Validate that the update agent request has valid tools, deployments, and compatible models.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    user_id = get_header_user_id(request)
    agent_id = request.path_params.get("agent_id")
    if not agent_id:
        logger.error(event="Agent ID is required.")
        raise HTTPException(status_code=400, detail="Agent ID is required.")

    agent = agent_crud.get_agent_by_id(session, agent_id, user_id)
    if not agent:
        logger.error(event="Agent not found", agent_id=agent_id)
        raise HTTPException(
            status_code=404, detail=f"Agent with ID {agent_id} not found."
        )

    if agent.user_id != user_id:
        logger.error(event="Agent does not belong to user.", agent_user_id=agent.user_id, user_id=user_id)
        raise HTTPException(
            status_code=401, detail=f"Agent with ID {agent_id} does not belong to user."
        )

    body = await request.json()
    # Validate tools
    tools = body.get("tools")
    if tools:
        for tool in tools:
            if tool not in get_available_tools():
                logger.error(event="Tool not found.", tool=tool)
                raise HTTPException(status_code=404, detail=f"Tool {tool} not found.")

    model, deployment = body.get("model"), body.get("deployment")
    # Model and deployment must be updated together to ensure compatibility
    if not model and deployment:
        logger.error(event="If updating an agent's deployment type, the model must also be provided.")
        raise HTTPException(
            status_code=400,
            detail="If updating an agent's deployment type, the model must also be provided.",
        )
    elif model and not deployment:
        logger.error(event="If updating an agent's model, the deployment must also be provided.")
        raise HTTPException(
            status_code=400,
            detail="If updating an agent's model, the deployment must also be provided.",
        )
    elif model and deployment:
        deployment_config = body.get("deployment_config")
        # Validate
        deployment_db, model_db = validate_deployment_model(deployment, model, session)
        if deployment_config:
            validate_deployment_config(deployment_config, deployment_db)


async def validate_create_update_model_request(session: DBSessionDep, request: Request):
    """
    Validate that the create model request has valid deployment.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    body = await request.json()
    deployment_id = body.get("deployment_id")
    if request.method == "POST" and not deployment_id:
        raise HTTPException(status_code=400, detail="deployment_id is required.")

    if deployment_id:
        deployment_db = deployment_crud.get_deployment(session, deployment_id)
        if not deployment_db:
            raise HTTPException(
                status_code=400,
                detail=f"Deployment {deployment_id} not found or is not available in the Database.",
            )


async def validate_create_deployment_request(session: DBSessionDep, request: Request):
    """
    Validate that the create deployment request is valid.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    body = await request.json()
    name = body.get("name")
    deployment = deployment_crud.get_deployment_by_name(session, name)
    if deployment:
        raise HTTPException(
            status_code=400, detail=f"Deployment {name} already exists."
        )

    deployment_class_name = body.get("deployment_class_name")
    try:
        class_name_validator(deployment_class_name)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Deployment class name {deployment_class_name} not found.",
        )


async def validate_organization_request(session: DBSessionDep, request: Request):
    """
    Validate create/update organization request.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """

    organization_id = request.path_params.get("org_id")
    # Organization ID is required for PUT requests
    if request.method == "PUT":
        if not organization_id:
            raise HTTPException(status_code=400, detail="Organization ID is required.")
        if organization_id and not organization_crud.get_organization(
            session, organization_id
        ):
            raise HTTPException(
                status_code=404,
                detail=f"Organization with ID: {organization_id} not found.",
            )
    body = await request.json()
    name = body.get("name")
    if not name and request.method == "POST":
        raise HTTPException(status_code=400, detail="Organization name is required.")
    check_organization = organization_crud.get_organization_by_name(session, name)
    if check_organization:
        raise HTTPException(
            status_code=400, detail=f"Organization with name: {name} already exists."
        )
