from urllib.parse import unquote_plus

from fastapi import HTTPException, Request

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.tools import AVAILABLE_TOOLS


def validate_user_header(request: Request):
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
    if deployment_name and (
        deployment_name not in AVAILABLE_MODEL_DEPLOYMENTS.keys()
        or not AVAILABLE_MODEL_DEPLOYMENTS[deployment_name].is_available
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Deployment {deployment_name} was not found, or is not available.",
        )


async def validate_chat_request(request: Request):
    """
    Validate that the request has the appropriate values in the body

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If the request does not have the appropriate values in the body
    """
    body = await request.json()
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
