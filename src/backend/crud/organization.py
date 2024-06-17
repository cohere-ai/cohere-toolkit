from sqlalchemy.orm import Session

from backend.database_models.organization import Organization
from backend.database_models.user import user_organization_association
from backend.schemas.organization import UpdateOrganization


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
            user_organization_association,
            Organization.id == user_organization_association.c.organization_id,
        )
        .filter(user_organization_association.c.user_id == user_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


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
