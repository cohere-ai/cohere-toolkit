
from sqlalchemy.orm import Session

from backend.database_models import Deployment
from backend.model_deployments.utils import class_name_validator
from backend.schemas.deployment import (
    DeploymentCreate,
    DeploymentDefinition,
    DeploymentUpdate,
)
from backend.services.transaction import validate_transaction


@validate_transaction
def create_deployment(db: Session, deployment: DeploymentCreate) -> Deployment:
    """
    Create a new deployment.

    Args:
        db (Session): Database session.
        deployment (DeploymentDefinition): Deployment data to be created.

    Returns:
        Deployment: Created deployment.
    """
    if deployment.deployment_class_name:
        class_name_validator(deployment.deployment_class_name)
    deployment = Deployment(**deployment.model_dump(exclude_none=True))
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return deployment


def get_deployment(db: Session, deployment_id: str) -> Deployment:
    """
    Get a deployment by ID.

    Args:
        db (Session): Database session.
        deployment_id (str): Deployment ID.

    Returns:
        Deployment: Deployment with the given ID.
    """
    return db.query(Deployment).filter(Deployment.id == deployment_id).first()


def get_deployment_by_name(db: Session, deployment_name: str) -> Deployment:
    """
    Get a deployment by deployment_name.

    Args:
        db (Session): Database session.
        deployment_name (str): Deployment Name.

    Returns:
        Deployment: Deployment with the given name.
    """
    return db.query(Deployment).filter(Deployment.name == deployment_name).first()


def get_deployment_by_class_name(db: Session, deployment_class_name: str) -> Deployment:
    """
    Get a deployment by deployment_class_name.

    Args:
        db (Session): Database session.
        deployment_class_name (str): Deployment Class Name.

    Returns:
        Deployment: Deployment with the given class name.
    """
    return db.query(Deployment).filter(Deployment.name == deployment_class_name).first()


def get_deployments(db: Session, offset: int = 0, limit: int = 100) -> list[Deployment]:
    """
    List all deployments.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of deployments to be listed.

    Returns:
        list[Deployment]: List of deployments.
    """
    return db.query(Deployment).offset(offset).limit(limit).all()


def get_available_deployments(
    db: Session, offset: int = 0, limit: int = 100
) -> list[Deployment]:
    """
    List all available deployments.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of deployments to be listed.

    Returns:
        list[Deployment]: List of available deployments.
    """
    all_deployments = db.query(Deployment).all()
    return [deployment for deployment in all_deployments if deployment.is_available][
        offset: offset + limit
    ]

@validate_transaction
def update_deployment(
    db: Session, deployment: Deployment, new_deployment: DeploymentUpdate
) -> Deployment:
    """
    Update a deployment by ID.

    Args:
        db (Session): Database session.
        deployment (Deployment): Deployment to be updated.
        new_deployment (Deployment): New deployment data.

    Returns:
        Deployment: Updated deployment.
    """
    for attr, value in new_deployment.model_dump(exclude_none=True).items():
        setattr(deployment, attr, value)
    db.commit()
    db.refresh(deployment)
    return deployment


@validate_transaction
def delete_deployment(db: Session, deployment_id: str) -> None:
    """
    Delete a deployment by ID.

    Args:
        db (Session): Database session.
        deployment_id (str): Deployment ID.
    """
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id)
    deployment.delete()
    db.commit()


@validate_transaction
def create_deployment_by_config(db: Session, deployment_config: DeploymentDefinition) -> Deployment:
    """
    Create a new deployment by config.

    Args:
        db (Session): Database session.
        deployment_config (DeploymentDefinition): Deployment config.

    Returns:
        Deployment: Created deployment.
    """
    deployment = Deployment(
        name=deployment_config.name,
        description="",
        default_deployment_config=deployment_config.config,
        deployment_class_name=deployment_config.class_name,
        is_community=deployment_config.is_community,
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return deployment

