"""Setup for Sybil."""

import pathlib
import subprocess
import sys
import tempfile
from doctest import ELLIPSIS

import pytest
from beartype import beartype
from sybil import Example, Sybil
from sybil.evaluators.python import pad
from sybil.parsers.rest import (
    CodeBlockParser,
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


class PytestEvaluator:
    """A :any:`Evaluator` for pytest examples."""

    def __call__(self, example: Example) -> None:
        """
        Run the code as a pytest test.
        """
        source = pad(
            source=example.parsed,
            line=example.line + example.parsed.line_offset,
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = pathlib.Path(tmp_dir) / "test_src.py"
            test_file.write_text(data=source)
            subprocess.check_output(
                args=[
                    sys.executable,
                    "-m",
                    "pytest",
                    test_file,
                    "--basetemp",
                    test_file.parent,
                ],
            )


run_code_sybil = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
    ],
    patterns=["*.rst", "*.py"],
)

pytest_sybil = Sybil(
    parsers=[CodeBlockParser(language="python", evaluator=PytestEvaluator())],
    patterns=["*.rst"],
)

sybils = run_code_sybil + pytest_sybil

pytest_collect_file = sybils.pytest()
