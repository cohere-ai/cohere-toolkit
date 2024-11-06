import base64

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import backend.crud.group as group_repo
import backend.crud.user as user_repo
from backend.config import Settings

scim = Settings().get('auth.scim')
encoded_auth = base64.b64encode(
    f"{scim.username}:{scim.password}".encode("utf-8")
).decode("utf-8")
scim_auth_header = {
    "Authorization": f"Basic {encoded_auth}",
}


def create_user_request(
    session_client: TestClient,
    user_name="testuser@company.com",
    external_id="23123123",
    email="thisispatrick@gmail.com",
):
    user_data_req = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": user_name,
        "name": {"givenName": "Test", "familyName": "User"},
        "emails": [{"primary": True, "value": email, "type": "work"}],
        "externalId": external_id,
        "locale": "en-US",
        "groups": [],
        "active": True,
    }

    return session_client.post(
        "/scim/v2/Users", json=user_data_req, headers=scim_auth_header
    )


def create_group_request(session_client: TestClient):
    request = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "displayName": "Test SCIMv2",
        "members": [],
    }

    return session_client.post(
        "/scim/v2/Groups", json=request, headers=scim_auth_header
    )


def test_create_user(session_client: TestClient, session: Session) -> None:
    response = create_user_request(session_client, email="tanzi66m@cohere.com")
    assert response.status_code == 201
    response_user = response.json()

    db_user = user_repo.get_user(session, response_user["id"])
    assert db_user is not None
    assert db_user.email == "tanzi66m@cohere.com"

    expected_user = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "externalId": "23123123",
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat(),
        },
    }

    assert response.status_code == 201
    assert response_user == expected_user


def test_get_user(session_client: TestClient, session: Session):
    response = session_client.get(
        "/scim/v2/Users/does-not-exist", headers=scim_auth_header
    )
    error_response = response.json()

    assert response.status_code == 404
    assert error_response == {
        "detail": "User not found",
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
    }

    response = create_user_request(session_client)
    response_user = response.json()
    assert response.status_code == 201

    response = session_client.get(
        f"/scim/v2/Users/{response_user['id']}", headers=scim_auth_header
    )
    user_response = response.json()

    db_user = user_repo.get_user_by_external_id(session, response_user["externalId"])
    assert db_user is not None

    expected_user = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "externalId": "23123123",
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat(),
        },
    }

    assert user_response == expected_user

    response = session_client.get(
        "/scim/v2/Users?filter=userName%20eq%20%22testuser@company.com%22&startIndex=1&count=100",
        headers=scim_auth_header,
    )
    assert response.status_code == 200
    list_user_response = response.json()
    user_response = list_user_response["Resources"][0]

    assert user_response == expected_user


def test_put_user(session_client: TestClient, session: Session):
    response = create_user_request(session_client, email="abcd@cc.com")
    response_user = response.json()
    user_id = response_user["id"]
    assert response.status_code == 201

    put_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": "test.user@okta.local",
        "name": {"givenName": "Another", "familyName": "User"},
        "active": True,
        "emails": [{"primary": True, "value": "tanzi22m@cohere.com", "type": "work"}],
        "meta": {"resourceType": "User"},
    }

    response = session_client.put(
        f"/scim/v2/Users/{user_id}", json=put_data, headers=scim_auth_header
    )
    response_user = response.json()
    db_user = user_repo.get_user(session, user_id)
    assert db_user is not None
    assert db_user.email == "tanzi22m@cohere.com"

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": "test.user@okta.local",
        "externalId": db_user.external_id,
        "active": True,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat(),
        },
    }

    assert response_user == expected_response


def test_patch_user(session_client: TestClient, session: Session):
    response = create_user_request(session_client)
    response_user = response.json()
    user_id = response_user["id"]
    assert response.status_code == 201

    patch_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [{"op": "replace", "value": {"active": False}}],
    }

    response = session_client.patch(
        f"/scim/v2/Users/{user_id}", json=patch_data, headers=scim_auth_header
    )
    response_user = response.json()

    db_user = user_repo.get_user(session, user_id)
    assert db_user is not None
    assert db_user.active is False

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": db_user.id,
        "userName": "testuser@company.com",
        "externalId": "23123123",
        "active": False,
        "meta": {
            "resourceType": "User",
            "created": db_user.created_at.isoformat(),
            "lastModified": db_user.updated_at.isoformat(),
        },
    }

    assert response_user == expected_response


def test_create_group(session_client: TestClient, session: Session):
    response = create_group_request(session_client)
    response_group = response.json()

    group = group_repo.get_group(session, response_group["id"])
    assert group is not None

    assert response.status_code == 201
    assert response_group == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group.id,
        "displayName": "Test SCIMv2",
        "members": [],
        "meta": {
            "resourceType": "Group",
            "created": group.created_at.isoformat(),
            "lastModified": group.updated_at.isoformat(),
        },
    }


def test_get_group(session_client: TestClient, session: Session):
    response = session_client.get(
        "/scim/v2/Groups/does-not-exist", headers=scim_auth_header
    )
    error_response = response.json()

    assert response.status_code == 404
    assert error_response == {
        "detail": "Group not found",
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
    }

    response = create_group_request(session_client)
    response_group = response.json()
    assert response.status_code == 201

    response = session_client.get(
        f"/scim/v2/Groups/{response_group['id']}", headers=scim_auth_header
    )
    group_response = response.json()

    db_group = group_repo.get_group(session, response_group["id"])
    assert db_group is not None

    expected_group = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": db_group.id,
        "displayName": "Test SCIMv2",
        "members": [],
        "meta": {
            "resourceType": "Group",
            "created": db_group.created_at.isoformat(),
            "lastModified": db_group.updated_at.isoformat(),
        },
    }

    assert group_response == expected_group

    response = session_client.get(
        "/scim/v2/Groups?filter=displayName%20eq%20%22Test%20SCIMv2%22&startIndex=1&count=100",
        headers=scim_auth_header,
    )
    assert response.status_code == 200
    list_group_response = response.json()
    group_response = list_group_response["Resources"][0]

    assert group_response == expected_group


def test_delete_group(session_client: TestClient, session: Session):
    response = create_group_request(session_client)
    response_group = response.json()
    group_id = response_group["id"]
    assert response.status_code == 201

    response = session_client.delete(
        f"/scim/v2/Groups/{group_id}", headers=scim_auth_header
    )
    assert response.status_code == 204

    response = session_client.get(
        f"/scim/v2/Groups/{group_id}", headers=scim_auth_header
    )
    error_response = response.json()

    assert response.status_code == 404
    assert error_response == {
        "detail": "Group not found",
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
    }


def test_update_group_name(session_client: TestClient, session: Session):
    response = create_group_request(session_client)
    response_group = response.json()
    group_id = response_group["id"]
    assert response.status_code == 201

    patch_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "replace",
                "value": {
                    "id": "abf4dd94-a4c0-4f67-89c9-76b03340cb9b",
                    "displayName": "New Group Name",
                },
            }
        ],
    }

    response = session_client.patch(
        f"/scim/v2/Groups/{group_id}", json=patch_data, headers=scim_auth_header
    )
    response_group = response.json()

    db_group = group_repo.get_group(session, group_id)
    assert db_group is not None

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group_id,
        "displayName": "New Group Name",
        "members": [],
        "meta": {
            "resourceType": "Group",
            "created": db_group.created_at.isoformat(),
            "lastModified": db_group.updated_at.isoformat(),
        },
    }

    assert response_group == expected_response


def test_add_users_to_group(session_client: TestClient, session: Session):
    response = create_group_request(session_client)
    response_group = response.json()
    group_id = response_group["id"]
    assert response.status_code == 201

    response = create_user_request(session_client)
    response_user = response.json()
    user_id = response_user["id"]
    assert response.status_code == 201

    patch_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "add",
                "path": "members",
                "value": [
                    {
                        "value": user_id,
                        "display": "test.user@okta.local",
                    }
                ],
            },
        ],
    }

    response = session_client.patch(
        f"/scim/v2/Groups/{group_id}", json=patch_data, headers=scim_auth_header
    )
    response_group = response.json()

    db_group = group_repo.get_group(session, group_id)
    assert db_group is not None

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group_id,
        "displayName": "Test SCIMv2",
        "members": [
            {
                "value": user_id,
                "display": "test.user@okta.local",
            }
        ],
        "meta": {
            "resourceType": "Group",
            "created": db_group.created_at.isoformat(),
            "lastModified": db_group.updated_at.isoformat(),
        },
    }

    assert response_group == expected_response


def test_replace_users_in_group(session_client: TestClient, session: Session):
    test_add_users_to_group(session_client, session)
    group = group_repo.get_group_by_name(session, "Test SCIMv2")

    response = create_user_request(
        session_client,
        user_name="test.user.new@okta.local",
        external_id="1234546",
        email="sponge@krusty.com",
    )
    response_user = response.json()
    user_id = response_user["id"]
    username = response_user["userName"]
    assert response.status_code == 201

    patch_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "replace",
                "path": "members",
                "value": [
                    {
                        "value": user_id,
                        "display": username,
                    },
                ],
            }
        ],
    }

    response = session_client.patch(
        f"/scim/v2/Groups/{group.id}", json=patch_data, headers=scim_auth_header
    )
    response_group = response.json()

    expected_response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group.id,
        "displayName": "Test SCIMv2",
        "members": [
            {
                "value": user_id,
                "display": "test.user.new@okta.local",
            }
        ],
        "meta": {
            "resourceType": "Group",
            "created": group.created_at.isoformat(),
            "lastModified": group.updated_at.isoformat(),
        },
    }

    assert response_group == expected_response


def test_scim_requests_are_authenticated(session_client: TestClient):
    response = session_client.get("/scim/v2/Users")
    assert response.status_code == 401

    response = session_client.post("/scim/v2/Users")
    assert response.status_code == 401

    response = session_client.patch("/scim/v2/Users/123")
    assert response.status_code == 401

    response = session_client.put("/scim/v2/Users/123")
    assert response.status_code == 401

    response = session_client.get("/scim/v2/Groups")
    assert response.status_code == 401

    response = session_client.post("/scim/v2/Groups")
    assert response.status_code == 401

    response = session_client.patch("/scim/v2/Groups/123")
    assert response.status_code == 401

    response = session_client.delete("/scim/v2/Groups/123")
    assert response.status_code == 401
