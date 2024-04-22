from backend.tools.function_tools.calculator import CalculatorFunctionTool


def test_calculator() -> None:
    calculator = CalculatorFunctionTool()
    result = calculator.call({"code": "2+2"})
    assert result == {"result": 4}


def test_calculator_invalid_syntax() -> None:
    calculator = CalculatorFunctionTool()
    result = calculator.call({"code": "2+"})
    assert result == {"result": "Parsing error - syntax not allowed."}
