# Writing Unit Test

This README will explain how to best write unit tests for the OSS Toolkit project.

To start, run `make dev` and `make run-tests`, these two commands should start your docker service and then run the suite of unit tests available.

## Using Fixtures

The main `tests/conftest.py` file will contain multiple fixtures that you can use within your unit tests, you will be able to use the `client` fixture to testing APIs without DB calls, or the `session` and `session_client` fixtures to test any API that requires interacting with the test DB.

You can create your own fixtures by importing `pytest` and decorating a method with `@pytest.fixture`, then anywhere in the test architecture you will be able to add that fixture to your unit test by adding the name of the fixture in your test method parameters.

For example,

```python
@pytest.fixture
def myfixture():
    yield something

def test_something(myfixture):
    ..
```

The fixtures and tests do not need to be in the same file, nor do they need to be imported. Pytest will handle that for you.

## Using Factories

To write tests that require any initial setup, you can use `factory_boy` Factories to create objects from any model in the database. See the `tests/factories` folder for examples. 

The `tests/factories/__init__.py` file will contain a `get_factory()` method that can be imported and used throughout the tests. To add a new factory, simply add a file under the `factories` folder that inherits from `BaseFactory`, and add it to the `FACTORY_MAPPING` dictionary in the `__init__` file.