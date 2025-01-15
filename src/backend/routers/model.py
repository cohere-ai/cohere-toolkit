from fastapi import APIRouter, Depends, HTTPException

from backend.config.routers import RouterName
from backend.crud import model as model_crud
from backend.database_models import Model
from backend.database_models.database import DBSessionDep
from backend.schemas.model import DeleteModel, ModelCreate, ModelUpdate
from backend.schemas.model import Model as ModelSchema
from backend.schemas.params.model import ModelIdPathParam
from backend.schemas.params.shared import PaginationQueryParams
from backend.services.request_validators import validate_create_update_model_request

router = APIRouter(
    prefix="/v1/models",
    tags=[RouterName.MODEL],
)

router.name = RouterName.MODEL


@router.post(
    "",
    response_model=ModelSchema,
    dependencies=[
        Depends(validate_create_update_model_request),
    ],
)
def create_model(
    model: ModelCreate,
    session: DBSessionDep
) -> Model:
    """
    Create a new model.
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
    model_id: ModelIdPathParam,
    new_model: ModelUpdate,
    session: DBSessionDep,
) -> ModelSchema:
    """
    Update a model by ID.

    Raises:
        HTTPException: If the model with the given ID is not found.
    """
    model = model_crud.get_model(session, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model_crud.update_model(session, model, new_model)


@router.get("/{model_id}", response_model=ModelSchema)
def get_model(
    model_id: ModelIdPathParam,
    session: DBSessionDep,
) -> ModelSchema:
    """
    Get a model by ID.
    """
    model = model_crud.get_model(session, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.get("", response_model=list[ModelSchema])
def list_models(
    page_params: PaginationQueryParams,
    session: DBSessionDep,
) -> list[ModelSchema]:
    """
    List all available models
    """
    return model_crud.get_models(session, page_params.offset, page_params.limit)


@router.delete("/{model_id}")
async def delete_model(
    model_id: ModelIdPathParam,
    session: DBSessionDep,
) -> DeleteModel:
    """
    Delete a model by ID.

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
