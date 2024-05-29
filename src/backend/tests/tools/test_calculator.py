from backend.tools import Calculator


def test_calculator() -> None:
    calculator = Calculator()
    result = calculator.call({"code": "2+2"})
    assert result == {"result": 4}


def test_calculator_invalid_syntax() -> None:
    calculator = Calculator()
    result = calculator.call({"code": "2+"})
    assert result == {"result": "Parsing error - syntax not allowed."}
