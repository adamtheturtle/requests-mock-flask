"""
Imports used only in type hints.

We have a separate file for these so that we can ignore this file in
pip-missing-reqs, as we want to have type hints for modules which are not
install requirements.
"""


import flask  # pragma: no cover
import httpretty  # pragma: no cover
import requests  # pragma: no cover
from requests_mock import request as requests_mock_request  # pragma: no cover
from requests_mock import (
    response as requests_mock_response,  # pragma: no cover
)

# from requests_mock.request import Request  # pragma: no cover
# from requests_mock.response import Context  # pragma: no cover

__all__ = [  # pragma: no cover
    "flask",
    "httpretty",
    "requests",
    "requests_mock_response",
    "requests_mock_request",
]
