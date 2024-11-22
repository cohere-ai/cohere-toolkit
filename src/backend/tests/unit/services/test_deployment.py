from backend.config.tools import Tool


def test_all_tools_have_id() -> None:
    for tool in Tool:
        assert tool.value.ID is not None
