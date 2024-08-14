from fastapi import APIRouter, Depends, HTTPException, Response

from backend.config.routers import RouterName
from backend.crud import model as model_crud
from backend.database_models import Model
from backend.database_models.database import DBSessionDep
from backend.schemas.model import DeleteModel
from backend.schemas.model import Model as ModelSchema
from backend.schemas.model import ModelCreate, ModelUpdate
from backend.services.request_validators import validate_create_update_model_request

router = APIRouter(
    prefix="/v1/models",
)

router.name = RouterName.MODEL


@router.post(
    "",
    response_model=ModelSchema,
    dependencies=[
        Depends(validate_create_update_model_request),
    ],
)
def create_model(model: ModelCreate, session: DBSessionDep) -> Model:
    """
    Create a new model.

    Args:
        model (ModelCreate): Model data to be created.
        session (DBSessionDep): Database session.

    Returns:
        ModelSchema: Created model.
    """
    return model_crud.create_model(session, model)


@router.put(
    "/{model_id}",
    response_model=ModelSchema,
    dependencies=[
        Depends(validate_create_update_model_request),
    ],
)
def update_model(
    model_id: str, new_model: ModelUpdate, session: DBSessionDep
) -> ModelSchema:
    """
    Update a model by ID.

    Args:
        model_id (str): Model ID.
        new_model (ModelCreateUpdate): New model data.
        session (DBSessionDep): Database session.

    Returns:
        ModelSchema: Updated model.

    Raises:
        HTTPException: If the model with the given ID is not found.
    """
    model = model_crud.get_model(session, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model_crud.update_model(session, model, new_model)


@router.get("/{model_id}", response_model=ModelSchema)
def get_model(model_id: str, session: DBSessionDep) -> ModelSchema:
    """
    Get a model by ID.

    Returns:
        Model: Model with the given ID.
    """
    model = model_crud.get_model(session, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.get("", response_model=list[ModelSchema])
def list_models(
    *, offset: int = 0, limit: int = 100, session: DBSessionDep
) -> list[ModelSchema]:
    """
    List all available models

    Returns:
        list[Model]: List of available models.
    """
    return model_crud.get_models(session, offset, limit)


@router.delete("/{model_id}")
async def delete_model(model_id: str, session: DBSessionDep) -> DeleteModel:
    """
    Delete a model by ID.

    Args:
        model_id (str): Model ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        DeleteModel: Empty response.

    Raises:
        HTTPException: If the model with the given ID is not found.
    """
    model = model_crud.get_model(session, model_id)

    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with ID: {model_id} not found."
        )

    model_crud.delete_model(session, model_id)

    return DeleteModel()
