from fastapi.testclient import TestClient


def test_list_auth_strategies(session_client: TestClient) -> None:
    response = session_client.get("/v1/auth_strategies")

    assert response.status_code == 200
    assert response.json() == [
        {
            "strategy": "Basic",
            "client_id": None,
            "authorization_endpoint": None,
            "pkce_enabled": False,
        },
        {
            "strategy": "Google",
            "client_id": "test",
            "authorization_endpoint": None,
            "pkce_enabled": False,
        },
        {
            "strategy": "OIDC",
            "client_id": "test",
            "authorization_endpoint": None,
            "pkce_enabled": False,
        },
    ]
