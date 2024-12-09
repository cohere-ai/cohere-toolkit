# ruff: noqa
from backend.scripts.cli.main import *  # NOQA

"""
These tests are boilerplate and do not test the actual functionality of the code.
They are only used to avoid breaking the codebase due to import errors.
"""


def test_show_examples():
    assert show_examples() is None


def test_wrap_up():
    assert wrap_up(["test"]) is None
