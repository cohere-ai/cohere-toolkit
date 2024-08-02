from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config.routers import RouterName
from backend.crud import agent as agent_crud
from backend.crud import organization as organization_crud
from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.organization import Organization as OrganizationModel
from backend.schemas import (
    CreateOrganization,
    DeleteOrganization,
    Organization,
    UpdateOrganization,
)
from backend.schemas.context import Context
from backend.services.auth.utils import get_header_user_id
from backend.services.context import get_context
from backend.services.request_validators import validate_organization_request

router = APIRouter(prefix="/v1/organizations")
router.name = RouterName.TOOL


@router.post(
    "",
    response_model=Organization,
    dependencies=[
        Depends(validate_organization_request),
    ],
)
def create_organization(
    organization: CreateOrganization,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Organization:
    """
    Create a new organization.

    Args:
        organization (CreateOrganization): Organization data
        session (DBSessionDep): Database session.

    Returns:
        Organization: Created organization.
    """
    organization_data = OrganizationModel(**organization.dict())

    return organization_crud.create_organization(session, organization_data)


@router.put(
    "/{organization_id}",
    response_model=Organization,
    dependencies=[
        Depends(validate_organization_request),
    ],
)
def update_organization(
    organization_id: str,
    new_organization: UpdateOrganization,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Organization:
    """
    Update organization by ID.

    Args:
        organization_id (str): Tool ID.
        new_organization (ToolUpdate): New organization data.
        session (DBSessionDep): Database session.

    Returns:
        Organization: Updated organization.

    """
    organization = organization_crud.get_organization(session, organization_id)
    return organization_crud.update_organization(
        session, organization, new_organization
    )


@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
) -> Organization:
    """
    Get a organization by ID.

    Args:
        organization_id (str): Tool ID.
        session (DBSessionDep): Database session.

    Returns:
        ManagedTool: Tool with the given ID.
    """
    organization = organization_crud.get_organization(session, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Model not found")
    return organization


@router.delete("/{organization_id}", response_model=DeleteOrganization)
def delete_organization(
    organization_id: str,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteOrganization:
    """
    Delete a organization by ID.

    Args:
        organization_id (str): Tool ID.
        session (DBSessionDep): Database session.

    Returns:
        DeleteOrganization: Organization deleted.
    """
    organization = organization_crud.get_organization(session, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Tool not found")
    organization_crud.delete_organization(session, organization_id)

    return DeleteOrganization()


@router.get("", response_model=list[Organization])
def list_organizations(
    request: Request,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[Organization]:
    """
    List all available organizations.

    Args:
        request (Request): Request object.
        session (DBSessionDep): Database session.

    Returns:
        list[ManagedTool]: List of available organizations.
    """
    all_organizations = organization_crud.get_organizations(session)
    return all_organizations
