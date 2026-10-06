"""Tests for helper usage with `responses`."""

from http import HTTPStatus

import requests
import responses
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock
from tests.usage.helpers import TIMEOUT_SECONDS


def test_context_manager() -> None:
    """
    It is possible to use the helper with a ``responses`` context
    manager.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    response = requests.Response()

    with responses.RequestsMock(
        assert_all_requests_are_fired=False,
    ) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = requests.get(
            url="http://www.example.com",
            timeout=TIMEOUT_SECONDS,
        )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


@responses.activate
def test_decorator() -> None:
    """It is possible to use the helper with a ``responses`` decorator."""
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    add_flask_app_to_mock(
        mock_obj=responses,
        flask_app=app,
        base_url="http://www.example.com",
    )

    response = requests.get(
        url="http://www.example.com",
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
