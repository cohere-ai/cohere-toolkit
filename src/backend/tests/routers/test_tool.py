from fastapi.testclient import TestClient

from backend.config.tools import AVAILABLE_TOOLS


def test_list_tools(client: TestClient) -> None:
    response = client.get("/v1/tools")
    assert response.status_code == 200
    for tool in response.json():
        assert tool["name"] in AVAILABLE_TOOLS.keys()

        # get tool that has the same name as the tool in the response
        tool_definition = AVAILABLE_TOOLS[tool["name"]]

        assert tool["kwargs"] == tool_definition.kwargs
        assert tool["is_visible"] == tool_definition.is_visible
        assert tool["is_available"] == tool_definition.is_available
        assert tool["error_message"] == tool_definition.error_message
        assert tool["category"] == tool_definition.category
        assert tool["description"] == tool_definition.description
