"""Setup for Sybil."""

import sys
from doctest import ELLIPSIS

import pytest
from beartype import beartype
from sybil import Sybil
from sybil.parsers.rest import (
    CodeBlockParser,
    DocTestParser,
    PythonCodeBlockParser,
)
from sybil_extras.evaluators.shell_evaluator import ShellCommandEvaluator


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Apply the beartype decorator to all collected test functions.
    """
    for item in items:
        if isinstance(item, pytest.Function):
            item.obj = beartype(obj=item.obj)


run_code_sybil = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
    ],
    patterns=["*.rst", "*.py"],
)

pytest_sybil = Sybil(
    parsers=[
        CodeBlockParser(
            language="python",
            evaluator=ShellCommandEvaluator(
                args=[sys.executable, "-m", "pytest"],
                tempfile_suffixes=[".py"],
                pad_file=True,
                write_to_file=False,
            ),
        ),
    ],
    patterns=["*.rst"],
)

sybils = run_code_sybil + pytest_sybil

pytest_collect_file = sybils.pytest()
