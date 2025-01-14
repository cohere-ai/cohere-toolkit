from sqlalchemy.orm import Session

from backend.database_models.model import Model
from backend.schemas.deployment import DeploymentDefinition
from backend.schemas.model import ModelCreate, ModelUpdate
from backend.services.logger.utils import LoggerFactory
from backend.services.transaction import validate_transaction

logger = LoggerFactory().get_logger()


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


def get_model_by_name(db: Session, model_name: str) -> Model | None:
    """
    Get a model by name.

    Args:
        db (Session): Database session.
        model_name (str): Model name.

    Returns:
        Model: Model with the given name.
    """
    return db.query(Model).filter(Model.name == model_name).first()


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


def create_model_by_config(db: Session, deployment_config: DeploymentDefinition, deployment_id: str, model: str | None) -> Model:
    """
    Create a new model by config if present

    Args:
        db (Session): Database session.
        deployment_config (DeploymentDefinition): A deployment definition for any kind of deployment.
        deployment_id (DeploymentDefinition): Deployment ID for a deployment from the DB.
        model (str): Optional model name that should have its data returned from this call.

    Returns:
        Model: Created model.
    """
    logger.debug(event="create_model_by_config", deployment_models=deployment_config.models, deployment_id=deployment_id, model=model)
    deployment_db_models = get_models_by_deployment_id(db, deployment_id)
    model_to_return = None
    for deployment_config_model in deployment_config.models:
        model_in_db = any(record.name == deployment_config_model for record in deployment_db_models)
        if not model_in_db:
            new_model = Model(
                name=deployment_config_model,
                cohere_name=deployment_config_model,
                deployment_id=deployment_id,
            )
            db.add(new_model)
            db.commit()
            if model == new_model.name:
                model_to_return = new_model

    return model_to_return
