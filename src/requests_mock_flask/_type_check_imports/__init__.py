"""
Imports used only in type hints.

We have a separate file for these so that we can ignore this file in
pip-missing-reqs, as we want to have type hints for modules which are not
install requirements.
"""

import flask  # pragma: no cover
import requests  # pragma: no cover
import requests_mock  # pragma: no cover

__all__ = [  # pragma: no cover
    'flask',
    'requests',
    'requests_mock',
]
