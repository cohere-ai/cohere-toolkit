from sqlalchemy.orm import Session

from backend.database_models import Agent, AgentDeploymentModel, Deployment
from backend.database_models.model import Model
from backend.schemas.model import ModelCreate, ModelUpdate
from backend.services.transaction import validate_transaction


@validate_transaction
def create_model(db: Session, model: ModelCreate) -> Model:
    """
    Create a new model.

    Args:
        db (Session): Database session.
        model (Model): Model data to be created.

    Returns:
        Model: Created model.
    """
    model = Model(**model.model_dump(exclude_none=True))
    db.add(model)
    db.commit()
    return model


def get_model(db: Session, model_id: str) -> Model | None:
    """
    Get a model by ID.

    Args:
        db (Session): Database session.
        model_id (str): Model ID.

    Returns:
        Model: Model with the given ID.
    """
    return db.query(Model).filter(Model.id == model_id).first()


def get_models(db: Session, offset: int = 0, limit: int = 100) -> list[Model]:
    """
    List all models.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of models to be listed.

    Returns:
        list[Model]: List of models.
    """
    return db.query(Model).offset(offset).limit(limit).all()


def get_models_by_deployment_id(
    db: Session, deployment_id: str, offset: int = 0, limit: int = 100
) -> list[Model]:
    """
    List all models deploymrent ID.

    Args:
        db (Session): Database session.
        deployment_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of models to be listed.

    Returns:
        list[Model]: List of models.
    """
    return (
        db.query(Model)
        .filter(Model.deployment_id == deployment_id)
        .order_by(Model.name)
        .limit(limit)
        .offset(offset)
        .all()
    )


@validate_transaction
def update_model(db: Session, model: Model, new_model: ModelUpdate) -> Model:
    """
    Update a model.

    Args:
        db (Session): Database session.
        model (Model): Model to be updated.
        new_model (Model): New model data.

    Returns:
        Model: Updated model.
    """
    for attr, value in new_model.model_dump(exclude_none=True).items():
        setattr(model, attr, value)
    db.commit()
    db.refresh(model)
    return model


@validate_transaction
def delete_model(db: Session, model_id: str) -> None:
    """
    Delete a model by ID.

    Args:
        db (Session): Database session.
        model_id (str): Model ID.
    """
    model = db.query(Model).filter(Model.id == model_id)
    model.delete()
    db.commit()


def get_models_by_agent_id(
    db: Session, agent_id: str, offset: int = 0, limit: int = 100
) -> list[Model]:
    """
    List all models by user id

    Args:
        db (Session): Database session.
        agent_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of models to be listed.

    Returns:
        list[Model]: List of models.
    """

    return (
        db.query(Model)
        .join(
            AgentDeploymentModel,
            agent_id == AgentDeploymentModel.agent_id,
        )
        .filter(Model.deployment_id == AgentDeploymentModel.deployment_id)
        .order_by(Model.name)
        .limit(limit)
        .offset(offset)
        .all()
    )
