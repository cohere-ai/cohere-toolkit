from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models.organization import Organization as OrganizationModel
from backend.schemas.organization import CreateOrganization, UpdateOrganization
from backend.tests.unit.factories import get_factory


def test_create_organization(session_client: TestClient, session: Session) -> None:
    organization = CreateOrganization(name="test organization")
    response = session_client.post("/v1/organizations", json=organization.model_dump())
    assert response.status_code == 200
    assert response.json()["name"] == organization.name


def test_create_organization_with_existing_name(
    session_client: TestClient, session: Session
) -> None:
    get_factory("Organization", session).create(name="test organization")
    new_organization = CreateOrganization(name="test organization")
    response = session_client.post("/v1/organizations", json=new_organization.model_dump())
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Organization with name: test organization already exists."
    }


def test_update_organization(session_client: TestClient, session: Session) -> None:
    organization = get_factory("Organization", session).create(name="test organization")
    new_organization = UpdateOrganization(name="new organization")
    response = session_client.put(
        f"/v1/organizations/{organization.id}", json=new_organization.model_dump()
    )
    assert response.status_code == 200
    assert response.json()["name"] == new_organization.name


def test_update_not_existing_organization(
    session_client: TestClient, session: Session
) -> None:
    new_organization = UpdateOrganization(name="new organization")
    response = session_client.put("/v1/organizations/123", json=new_organization.model_dump())
    assert response.status_code == 404
    assert response.json() == {"detail": "Organization with ID: 123 not found."}


def test_get_organization(session_client: TestClient, session: Session) -> None:
    organization = get_factory("Organization", session).create(name="test organization")
    response = session_client.get(f"/v1/organizations/{organization.id}")
    assert response.status_code == 200
    assert response.json()["name"] == organization.name


def test_list_organizations(session_client: TestClient, session: Session) -> None:
    session.query(OrganizationModel).delete()
    for i in range(5):
        get_factory("Organization", session).create(name=f"test organization {i}")

    response = session_client.get("/v1/organizations")
    results = response.json()
    assert response.status_code == 200
    assert len(results) == 5


def test_delete_organization(session_client: TestClient, session: Session) -> None:
    organization = get_factory("Organization", session).create(name="test organization")
    response = session_client.delete(f"/v1/organizations/{organization.id}")
    assert response.status_code == 200
    assert response.json() == {}


def test_list_organization_users(session_client: TestClient, session: Session) -> None:
    organization = get_factory("Organization", session).create(name="test organization")
    for i in range(5):
        user = get_factory("User", session).create(fullname=f"test user {i}")
        organization.users.append(user)

    response = session_client.get(f"/v1/organizations/{organization.id}/users")
    results = response.json()
    assert response.status_code == 200
    assert len(results) == 5
    results = sorted(results, key=lambda x: x["fullname"])
    for i, result in enumerate(results):
        assert result["fullname"] == f"test user {i}"
