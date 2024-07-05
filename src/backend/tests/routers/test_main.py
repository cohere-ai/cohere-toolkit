from fastapi.testclient import TestClient


def test_global_exception_handler(session_client: TestClient):
    response = session_client.get("/error")
    assert response.status_code == 500
    assert response.json() == {
        "message": (
            "Failed method GET at URL http://testserver/error. Exception message is Exception('This is a test exception')."
        )
    }

def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
