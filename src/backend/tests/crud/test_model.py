import pytest

from backend.crud import model as model_crud
from backend.database_models.model import Model
from backend.schemas.model import Model as ModelSchema
from backend.schemas.model import ModelCreate, ModelUpdate
from backend.tests.factories import get_factory


def test_create_model(session, deployment):
    model_data = ModelCreate(
        name="Test Model",
        cohere_name="Test Cohere Model",
        description="Test Description",
        deployment_id=deployment.id,
    )

    model = model_crud.create_model(session, model_data)
    assert model.name == model_data.name
    assert model.cohere_name == model_data.cohere_name
    assert model.description == model_data.description

    model = model_crud.get_model(session, model.id)
    assert model.name == model_data.name


def test_get_model(session, deployment):
    model = get_factory("Model", session).create(
        name="Test Model", deployment=deployment
    )
    retrieved_model = model_crud.get_model(session, model.id)
    assert retrieved_model.id == model.id
    assert retrieved_model.name == model.name


def test_fail_get_nonexistent_model(session):
    model = model_crud.get_model(session, "123")
    assert model is None


def test_list_models(session, deployment):
    # Delete default models
    session.query(Model).delete()
    _ = get_factory("Model", session).create(name="Test Model", deployment=deployment)

    models = model_crud.get_models(session)
    assert len(models) == 1
    assert models[0].name == "Test Model"


def test_list_models_empty(session):
    # Delete default models
    session.query(Model).delete()
    models = model_crud.get_models(session)
    assert len(models) == 0


def test_list_models_with_pagination(session, deployment):
    # Delete default models
    session.query(Model).delete()
    for i in range(10):
        _ = get_factory("Model", session).create(
            name=f"Test Model {i}", deployment=deployment
        )

    models = model_crud.get_models(session, offset=5, limit=5)
    assert len(models) == 5
    models.sort(key=lambda x: x.name)
    for i, model in enumerate(models):
        assert model.name == f"Test Model {i + 5}"


def test_get_models_by_deployment_id(session, deployment):
    for i in range(10):
        model = get_factory("Model", session).create(
            name=f"Test Model {i}", deployment=deployment
        )

    models = model_crud.get_models_by_deployment_id(session, deployment.id)

    assert len(models) == 10
    for i, model in enumerate(models):
        assert model.name == f"Test Model {i}"


def test_get_models_by_deployment_id_empty(session, deployment):
    models = model_crud.get_models_by_deployment_id(session, deployment.id)
    assert len(models) == 0


def test_get_models_by_deployment_id_with_pagination(session, deployment):
    for i in range(10):
        model = get_factory("Model", session).create(
            name=f"Test Model {i}", deployment=deployment
        )

    models = model_crud.get_models_by_deployment_id(
        session, deployment.id, offset=5, limit=5
    )
    assert len(models) == 5

    for i, model in enumerate(models):
        assert model.name == f"Test Model {i + 5}"


def test_update_model(session, deployment):
    model = get_factory("Model", session).create(
        name="Sagemaker model", deployment=deployment
    )
    another_deployment = get_factory("Deployment", session).create()

    new_model_data = ModelUpdate(
        name="Cohere",
        cohere_name="Cohere",
        description="Cohere",
        deployment_id=another_deployment.id,
    )

    updated_model = model_crud.update_model(session, model, new_model_data)

    assert updated_model.name == new_model_data.name
    assert updated_model.cohere_name == new_model_data.cohere_name
    assert updated_model.description == new_model_data.description
    assert updated_model.deployment_id == new_model_data.deployment_id

    model = model_crud.get_model(session, model.id)
    assert model.name == new_model_data.name
    assert model.cohere_name == new_model_data.cohere_name
    assert model.description == new_model_data.description
    assert model.deployment_id == new_model_data.deployment_id


def test_update_model_partial(session, deployment):
    model = get_factory("Model", session).create(
        name="Test Model U", deployment=deployment
    )

    new_model_data = ModelUpdate(name="Cohere", cohere_name="Cohere")

    updated_model = model_crud.update_model(session, model, new_model_data)

    assert updated_model.name == new_model_data.name
    assert updated_model.cohere_name == new_model_data.cohere_name
    assert updated_model.description == model.description
    assert updated_model.deployment_id == model.deployment_id

    model = model_crud.get_model(session, model.id)
    assert model.name == new_model_data.name
    assert model.cohere_name == new_model_data.cohere_name
    assert model.description == model.description
    assert model.deployment_id == model.deployment_id


def test_do_not_update_model(session, deployment):
    model = get_factory("Model", session).create(
        name="Test Model", deployment=deployment
    )

    new_model_data = ModelUpdate(name="Test Model")

    updated_model = model_crud.update_model(session, model, new_model_data)
    assert updated_model.name == model.name


def test_delete_model(session, deployment):
    model = get_factory("Model", session).create(deployment=deployment)

    model_crud.delete_model(session, model.id)

    model = model_crud.get_model(session, model.id)
    assert model is None


def test_delete_nonexistent_model(session):
    model_crud.delete_model(session, "123")  # no error
    model = model_crud.get_model(session, "123")
    assert model is None


def test_get_models_by_agent_id(session, user, deployment):
    agent = get_factory("Agent", session).create(user=user)
    for i in range(10):
        model = get_factory("Model", session).create(
            name=f"Test Model {i}", deployment=deployment
        )

        agent_deployment_model = get_factory("AgentDeploymentModel", session).create(
            agent=agent, deployment=deployment, model=model
        )

    models = model_crud.get_models_by_agent_id(session, agent.id)

    assert len(models) == 10
    for i, model in enumerate(models):
        assert model.name == f"Test Model {i}"
