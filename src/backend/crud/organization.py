from sqlalchemy.orm import Session

from backend.database_models import Agent
from backend.database_models.organization import Organization
from backend.database_models.user import User, UserOrganizationAssociation
from backend.schemas.organization import CreateOrganization, UpdateOrganization
from backend.services.transaction import validate_transaction


@validate_transaction
def create_organization(db: Session, organization: Organization) -> Organization:
    """ "
    Create a new organization.

    Args:
        db (Session): Database session.
        organization (Organization): Organization data to be created.

    Returns:
        Organization: Created organization.
    """
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def get_organization(db: Session, organization_id: str) -> Organization:
    """
    Get a organization by ID.

    Args:
        db (Session): Database session.
        organization_id (str): Organization ID.

    Returns:
        Organization: Organization with the given ID.
    """
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organization_by_name(db: Session, name: str) -> Organization:
    """
    Get a organization by name.

    Args:
        db (Session): Database session.
        name (str): Organization name.

    Returns:
        Organization: Organization with the given name.
    """
    return db.query(Organization).filter(Organization.name == name).first()


def get_organizations(
    db: Session, offset: int = 0, limit: int = 100
) -> list[Organization]:
    """
    List all organizations.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of organizations to be listed.

    Returns:
        list[Organization]: List of organizations.
    """
    return db.query(Organization).offset(offset).limit(limit).all()


def get_organizations_by_user_id(
    db: Session, user_id: str, offset: int = 0, limit: int = 100
) -> list[Organization]:
    """
    List all organizations by user id

    Args:
        db (Session): Database session.
        user_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of organizations to be listed.

    Returns:
        list[Organization]: List of organizations.
    """
    return (
        db.query(Organization)
        .join(
            UserOrganizationAssociation,
            Organization.id == UserOrganizationAssociation.organization_id,
        )
        .filter(UserOrganizationAssociation.user_id == user_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_organizations_by_agent_id(
    db: Session, agent_id: str, offset: int = 0, limit: int = 100
) -> list[Organization]:
    """
    List all organizations by agent id

    Args:
        db (Session): Database session.
        agent_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of organizations to be listed.

    Returns:
        list[Organization]: List of organizations.
    """
    return (
        db.query(Organization)
        .join(Agent, Organization.id == Agent.organization_id)
        .filter(Agent.id == agent_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


@validate_transaction
def update_organization(
    db: Session, organization: Organization, new_organization: UpdateOrganization
) -> Organization:
    """
    Update a organization by ID.

    Args:
        db (Session): Database session.
        organization (Organization): Organization to be updated.
        new_organization (Organization): New organization data.

    Returns:
        Organization: Updated organization.
    """
    for attr, value in new_organization.model_dump(exclude_none=True).items():
        setattr(organization, attr, value)
    db.commit()
    db.refresh(organization)
    return organization


@validate_transaction
def delete_organization(db: Session, organization_id: str) -> None:
    """
    Delete a organization by ID.

    Args:
        db (Session): Database session.
        organization_id (str): Organization ID.
    """
    organization = db.query(Organization).filter(Organization.id == organization_id)
    organization.delete()
    db.commit()


@validate_transaction
def add_user_to_organization(db: Session, user_id: str, organization_id: str) -> None:
    """
    Add a user to an organization.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        organization_id (str): Organization ID.
    """
    user_organization_association = UserOrganizationAssociation(
        user_id=user_id, organization_id=organization_id
    )
    db.add(user_organization_association)
    db.commit()


@validate_transaction
def remove_user_from_organization(
    db: Session, user_id: str, organization_id: str
) -> None:
    """
    Remove a user from an organization.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        organization_id (str): Organization ID.
    """
    user_organization_association = (
        db.query(UserOrganizationAssociation)
        .filter(
            UserOrganizationAssociation.user_id == user_id,
            UserOrganizationAssociation.organization_id == organization_id,
        )
        .first()
    )
    if user_organization_association:
        db.delete(user_organization_association)
        db.commit()


def get_users_by_organization_id(
    db: Session, organization_id: str, offset: int = 0, limit: int = 100
) -> list[User]:
    """
    List all users by organization ID.

    Args:
        db (Session): Database session.
        organization_id (str): Organization ID.
        offset (int): Offset to start the list.
        limit (int): Limit of users to be listed.

    Returns:
        list[User]: List of users.
    """
    return (
        db.query(User)
        .join(
            UserOrganizationAssociation,
            User.id == UserOrganizationAssociation.user_id,
        )
        .filter(UserOrganizationAssociation.organization_id == organization_id)
        .limit(limit)
        .offset(offset)
        .all()
    )
