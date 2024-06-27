from fastapi.testclient import TestClient


def test_list_auth_strategies(session_client: TestClient) -> None:
    response = session_client.get("/v1/auth_strategies")

    assert response.status_code == 200
    strategies = response.json()

    fields = ["strategy", "client_id", "authorization_endpoint", "pkce_enabled"]
    for strategy in strategies:
        for field in fields:
            assert field in strategy
