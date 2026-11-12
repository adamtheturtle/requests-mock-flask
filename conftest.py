"""Setup for Sybil."""

from collections.abc import Callable
from doctest import ELLIPSIS
from pathlib import Path

import pytest
from sybil import Sybil
from sybil.integration.pytest import pytest_integration as _pytest_integration
from sybil.parsers.rest import DocTestParser, PythonCodeBlockParser

sybil: Sybil = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
    ],
    patterns=["*.rst", "*.py"],
)

pytest_collect_file: Callable[[Path, pytest.Collector], pytest.File | None] = (
    _pytest_integration(sybil)
)
