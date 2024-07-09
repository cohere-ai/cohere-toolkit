import pytest

from backend.tools import Calculator


@pytest.mark.asyncio
async def test_calculator() -> None:
    calculator = Calculator()
    result = await calculator.call({"code": "2+2"})
    assert result == {"text": 4}


@pytest.mark.asyncio
async def test_calculator_invalid_syntax() -> None:
    calculator = Calculator()
    result = await calculator.call({"code": "2+"})
    assert result == {"text": "Parsing error - syntax not allowed."}
