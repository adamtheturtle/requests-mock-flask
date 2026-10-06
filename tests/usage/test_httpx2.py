"""Tests for helper usage with `httpx2`.

Tests for using the helper with ``respx`` and ``httpx2``.
``pytest-httpx2`` registers the ``httpcore2`` mocker with ``respx``.
"""

from http import HTTPStatus

import httpx2
import pytest
import respx
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock


def test_context_manager() -> None:
    """
    It is possible to use the helper with a ``respx`` context
    manager which intercepts ``httpx2`` requests.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    with respx.mock(assert_all_called=False, using="httpcore2") as m:
        add_flask_app_to_mock(
            mock_obj=m,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = httpx2.get(url="http://www.example.com")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


@pytest.mark.httpx2(assert_all_called=False)
def test_fixture(httpx2_mock: respx.MockRouter) -> None:
    """
    It is possible to use the helper with the ``pytest-httpx2``
    fixture, configured with its marker.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    add_flask_app_to_mock(
        mock_obj=httpx2_mock,
        flask_app=app,
        base_url="http://www.example.com",
    )

    response = httpx2.get(url="http://www.example.com")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
