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
from sybil.parsers.rest.lexers import DirectiveInCommentLexer, DirectiveLexer


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Apply the beartype decorator to all collected test functions.
    """
    for item in items:
        if isinstance(item, pytest.Function):
            item.obj = beartype(obj=item.obj)


# We create a new parser for Python which is the same as the default one
# but with a lexer which does not pick up `.. code::` blocks.
#
# This allows us to have some code blocks which are not picked up.
python_code_block_parser = PythonCodeBlockParser()
lexers = [
    DirectiveLexer(directive=r"code-block"),
    DirectiveInCommentLexer(directive=r"(invisible-)?code(-block)?"),
]
python_code_block_parser.lexers.clear()
python_code_block_parser.lexers.extend(lexers)


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        python_code_block_parser,
        CaptureParser(),
    ],
    patterns=["*.rst", "*.py"],
).pytest()
