import pytest

from backend.schemas.context import Context
from backend.tools import Calculator


@pytest.mark.asyncio
async def test_calculator() -> None:
    ctx = Context()
    calculator = Calculator()
    result = await calculator.call({"code": "2+2"}, ctx)
    assert result == {"text": 4}


@pytest.mark.asyncio
async def test_calculator_invalid_syntax() -> None:
    ctx = Context()
    calculator = Calculator()
    result = await calculator.call({"code": "2+"}, ctx)

    assert result == [{'details': 'parse error [column 2]: parity, expression: 2+', 'success': False, 'text': 'Error calling tool toolkit_calculator.', 'type': 'other'}]
