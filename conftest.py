"""Setup for Sybil."""

from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.rest import DocTestParser, PythonCodeBlockParser

sybil = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
    ],
    patterns=["*.rst", "*.py"],
)

pytest_collect_file = sybil.pytest()
