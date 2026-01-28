"""Setup for Sybil."""

import sys
import uuid
from doctest import ELLIPSIS
from pathlib import Path

import pytest
from beartype import beartype
from sybil import Example, Sybil
from sybil.parsers.rest import (
    CodeBlockParser,
    DocTestParser,
    PythonCodeBlockParser,
)
from sybil_extras.evaluators.shell_evaluator import ShellCommandEvaluator


def _make_temp_file_path(*, example: Example) -> Path:
    """Create a temporary file path for an example with ``.py`` suffix."""
    return Path(example.path).parent / f"_sybil_example_{uuid.uuid4().hex}.py"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply the beartype decorator to all collected test functions."""
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
                temp_file_path_maker=_make_temp_file_path,
                pad_file=True,
                write_to_file=False,
                use_pty=False,
            ),
        ),
    ],
    patterns=["*.rst"],
)

sybils = run_code_sybil + pytest_sybil

pytest_collect_file = sybils.pytest()
