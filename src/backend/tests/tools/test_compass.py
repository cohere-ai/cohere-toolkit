from backend.tools import CompassTool


def test_calculator() -> None:
    compass = CompassTool()
    result = compass.call({"action": compass.ValidActions.CREATE_INDEX})
    assert result == {"text": 4}
