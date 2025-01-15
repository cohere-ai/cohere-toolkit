from fastapi import APIRouter, Depends, HTTPException

from backend.config.routers import RouterName
from backend.crud import organization as organization_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.organization import Organization as OrganizationModel
from backend.schemas import (
    CreateOrganization,
    DeleteOrganization,
    Organization,
    UpdateOrganization,
)
from backend.schemas.context import Context
from backend.schemas.params.organization import OrganizationIdPathParam
from backend.schemas.user import User
from backend.services.context import get_context
from backend.services.request_validators import validate_organization_request

router = APIRouter(
    prefix="/v1/organizations",
    tags=[RouterName.ORGANIZATION],
)
router.name = RouterName.ORGANIZATION


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
    """
    organization_data = OrganizationModel(**organization.model_dump())

    return organization_crud.create_organization(session, organization_data)


@router.put(
    "/{organization_id}",
    response_model=Organization,
    dependencies=[
        Depends(validate_organization_request),
    ],
)
def update_organization(
    organization_id: OrganizationIdPathParam,
    new_organization: UpdateOrganization,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Organization:
    """
    Update organization by ID.
    """
    organization = organization_crud.get_organization(session, organization_id)
    return organization_crud.update_organization(
        session, organization, new_organization
    )


@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: OrganizationIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> Organization:
    """
    Get a organization by ID.
    """
    organization = organization_crud.get_organization(session, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.delete("/{organization_id}", response_model=DeleteOrganization)
def delete_organization(
    organization_id: OrganizationIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteOrganization:
    """
    Delete a organization by ID.
    """
    organization = organization_crud.get_organization(session, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization_crud.delete_organization(session, organization_id)

    return DeleteOrganization()


@router.get("", response_model=list[Organization])
def list_organizations(
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[Organization]:
    """
    List all available organizations.
    """
    all_organizations = organization_crud.get_organizations(session)
    return all_organizations


@router.get("/{organization_id}/users", response_model=list[User])
def get_organization_users(
    organization_id: OrganizationIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[User]:
    """
    Get organization users by ID.
    """
    organization = organization_crud.get_organization(session, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization.users
