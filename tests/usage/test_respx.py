"""Tests for helper usage with `respx`."""

from http import HTTPStatus

import httpx
import respx
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock


def test_context_manager() -> None:
    """
    It is possible to use the helper with a ``respx`` context
    manager.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    with respx.mock(assert_all_called=False) as respx_mock:
        add_flask_app_to_mock(
            mock_obj=respx_mock,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = httpx.get(url="http://www.example.com")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


@respx.mock(assert_all_called=False)
def test_decorator(respx_mock: respx.MockRouter) -> None:
    """
    It is possible to use the helper with a ``respx``
    decorator.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    add_flask_app_to_mock(
        mock_obj=respx_mock,
        flask_app=app,
        base_url="http://www.example.com",
    )

    response = httpx.get(url="http://www.example.com")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
