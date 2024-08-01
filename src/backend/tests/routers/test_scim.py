from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import backend.crud.user as user_repo


def create_user_request(session_client: TestClient):
    user_data_req = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "testuser@company.com",
        "name": {
            "givenName": "Test",
            "familyName": "User"
        },
        "externalId": "23123123",
        "locale": "en-US",
        "groups": [],
        "active": True
    }

    response = session_client.post("/scim/v2/Users", json=user_data_req)
    return response


def test_create_user(session_client: TestClient, session: Session) -> None:
    response = create_user_request(session_client)
    response_user = response.json()

    db_user = user_repo.get_user_by_external_id(session, response_user["externalId"])
    assert db_user is not None

    expected_user = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
        ],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "name": {
            "givenName": "Test",
            "familyName": "User"
        },
        "externalId": "23123123",
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat()
        }
    }

    assert response.status_code == 201
    assert response_user == expected_user

    response = create_user_request(session_client)
    error_response = response.json()

    assert response.status_code == 409
    assert error_response == {
        "detail": "User already exists in the database.",
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"]
    }


def test_get_user(session_client: TestClient, session: Session):
    response = session_client.get("/scim/v2/Users/does-not-exist")
    error_response = response.json()

    assert response.status_code == 404
    assert error_response == {
        "detail": "User not found",
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"]
    }

    response = create_user_request(session_client)
    response_user = response.json()
    assert response.status_code == 201

    response = session_client.get(f"/scim/v2/Users/{response_user['id']}")
    user_response = response.json()

    db_user = user_repo.get_user_by_external_id(session, response_user["externalId"])
    assert db_user is not None

    expected_user = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
        ],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "name": {
            "givenName": "Test",
            "familyName": "User"
        },
        "externalId": "23123123",
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat()
        }
    }

    assert user_response == expected_user


def test_put_user(session_client: TestClient, session: Session):
    response = create_user_request(session_client)
    response_user = response.json()
    user_id = response_user["id"]
    assert response.status_code == 201

    put_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": "test.user@okta.local",
        "name": {
            "givenName": "Another",
            "familyName": "User"
        },
        "active": True,
        "meta": {
            "resourceType": "User"
        }
    }

    response = session_client.put(f"/scim/v2/Users/{user_id}", json=put_data)
    response_user = response.json()

    db_user = user_repo.get_user(session, user_id)
    assert db_user is not None

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": "test.user@okta.local",
        "name": {
            "givenName": "Another",
            "familyName": "User"
        },
        "externalId": db_user.external_id,
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat()
        }
    }

    assert response_user == expected_response


def test_patch_user(session_client: TestClient, session: Session):
    response = create_user_request(session_client)
    response_user = response.json()
    user_id = response_user["id"]
    assert response.status_code == 201

    patch_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [{
            "op": "replace",
            "value": {
                "active": False
            }
        }]
    }

    response = session_client.patch(f"/scim/v2/Users/{user_id}", json=patch_data)
    response_user = response.json()

    db_user = user_repo.get_user(session, user_id)
    assert db_user is not None
    assert db_user.active is False

    expected_response = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
        ],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "name": {
            "givenName": "Test",
            "familyName": "User"
        },
        "externalId": "23123123",
        "active": False,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat()
        }
    }

    assert response_user == expected_response
