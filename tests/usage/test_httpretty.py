"""Tests for helper usage with `httpretty`.

Tests for using the helper with HTTPretty.

We only test one way of using the helper with HTTPretty, because the
other ways also pass in the HTTPretty module.
"""

from http import HTTPStatus

import httpretty
import requests
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock
from tests.usage.helpers import TIMEOUT_SECONDS


def test_use() -> None:
    """It is possible to use the helper with HTTPretty."""
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    with httpretty.enabled():
        add_flask_app_to_mock(
            mock_obj=httpretty,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = requests.get(
            url="http://www.example.com",
            timeout=TIMEOUT_SECONDS,
        )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
