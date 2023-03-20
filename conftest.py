"""Setup for Sybil."""

from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.rest import (
    CaptureParser,
    DocTestParser,
    PythonCodeBlockParser,
)

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        CaptureParser(),
    ],
    patterns=["*.rst", "*.py"],
).pytest()
