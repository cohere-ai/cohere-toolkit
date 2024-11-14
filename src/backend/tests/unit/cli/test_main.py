# ruff: noqa
from backend.cli.main import *  # NOQA
from fastapi.testclient import TestClient

"""
These tests are boilerplate and do not test the actual functionality of the code.
They are only used to avoid breaking the codebase due to import errors.
"""

def test_global_exception_handler(error_client: TestClient):
    response = error_client.get("/error")

    assert response.status_code == 500
    assert response.json() == {
        "message": "Failed method GET at URL http://testserver/error. Exception message is Exception('Test exception')."
    }

def test_show_examples():
    assert show_examples() is None


def test_wrap_up():
    assert wrap_up(["test"]) is None
