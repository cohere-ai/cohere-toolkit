import os

import pytest

from backend.services.compass import Compass

is_compass_env_set = all(
    os.getenv(var) is not None
    for var in [
        "COHERE_COMPASS_API_URL",
        "COHERE_COMPASS_PARSER_URL",
        "COHERE_COMPASS_USERNAME",
        "COHERE_COMPASS_PASSWORD",
    ]
)


@pytest.mark.skipif(
    not is_compass_env_set, reason="Compass environment variables are not set"
)
def test_compass() -> None:
    compass = Compass()
    result = compass.invoke(
        action=Compass.ValidActions.CREATE_INDEX, parameters={"index": "foobar"}
    )
    assert result.result is None
    assert result.result is None
