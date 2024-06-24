from backend.services.compass import Compass


def test_calculator() -> None:
    compass = Compass()
    result = compass.invoke(
        action=Compass.ValidActions.CREATE_INDEX, parameters={"index": "foobar"}
    )
    assert result.result is None
    assert result.result is None
