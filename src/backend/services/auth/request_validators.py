from fastapi import HTTPException, Request

from backend.services.auth.jwt import JWTService


def validate_authorization(request: Request):
    """
    Validate that the request has the `Authorization` header, used for requests
    that require authentication.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If no `Authorization` header.

    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    scheme, token = authorization.split(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    decoded = JWTService().decode_jwt(token)

    if not decoded or "context" not in decoded:
        raise HTTPException(
            status_code=401, detail="Bearer token is invalid or expired."
        )

    return decoded["context"]
