"""Setup for Sybil."""

from doctest import ELLIPSIS

import pytest
from beartype import beartype
from sybil import Sybil
from sybil.parsers.rest import (
    CaptureParser,
    DocTestParser,
    PythonCodeBlockParser,
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Apply the beartype decorator to all collected test functions.
    """
    for item in items:
        if isinstance(item, pytest.Function):
            item.obj = beartype(obj=item.obj)


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        CaptureParser(),
    ],
    patterns=["*.rst", "*.py"],
).pytest()
