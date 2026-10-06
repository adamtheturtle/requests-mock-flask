"""Tests for helper usage with `requests_mock`."""

from http import HTTPStatus

import requests
import requests_mock as req_mock
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock
from tests.usage.constants import TIMEOUT_SECONDS


def test_context_manager() -> None:
    """
    It is possible to use the helper with a ``requests_mock``
    context
    manager.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    with req_mock.Mocker() as resp_m:
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


def test_fixture(requests_mock: req_mock.Mocker) -> None:
    """
    It is possible to use the helper with a ``requests_mock``
    fixture.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    add_flask_app_to_mock(
        mock_obj=requests_mock,
        flask_app=app,
        base_url="http://www.example.com",
    )

    response = requests.get(
        url="http://www.example.com",
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code == HTTPStatus.OK


def test_adapter() -> None:
    """
    It is possible to use the helper with a ``requests_mock``
    adapter.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    session = requests.Session()
    adapter = req_mock.Adapter()
    session.mount(prefix="mock", adapter=adapter)

    add_flask_app_to_mock(
        mock_obj=adapter,
        flask_app=app,
        base_url="mock://www.example.com",
    )

    response = session.get(url="mock://www.example.com")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
