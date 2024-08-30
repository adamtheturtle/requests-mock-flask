"""
Tests for ways the helper can be used.
"""

from http import HTTPStatus
from typing import Final

import httpretty  # type: ignore[import-untyped]
import requests
import requests_mock as req_mock
import responses
from flask import Flask

from requests_mock_flask import add_flask_app_to_mock

# We use a high timeout to allow interactive debugging while requests are being
# made.
_TIMEOUT_SECONDS: Final[int] = 120


class TestResponses:
    """
    Tests for using the helper with ``responses``.
    """

    @staticmethod
    def test_context_manager() -> None:
        """
        It is possible to use the helper with a ``responses`` context manager.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
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
                timeout=_TIMEOUT_SECONDS,
            )

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"

    @staticmethod
    @responses.activate
    def test_decorator() -> None:
        """
        It is possible to use the helper with a ``responses`` decorator.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
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
            timeout=_TIMEOUT_SECONDS,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"


class TestRequestsMock:
    """
    Tests for using the helper with ``requests_mock``.
    """

    @staticmethod
    def test_context_manager() -> None:
        """
        It is possible to use the helper with a ``requests_mock`` context
        manager.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
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
                timeout=_TIMEOUT_SECONDS,
            )

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"

    @staticmethod
    def test_fixture(requests_mock: req_mock.Mocker) -> None:
        """
        It is possible to use the helper with a ``requests_mock`` fixture.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
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
            timeout=_TIMEOUT_SECONDS,
        )

        assert response.status_code == HTTPStatus.OK

    @staticmethod
    def test_adapter() -> None:
        """
        It is possible to use the helper with a ``requests_mock`` adapter.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
        def _() -> str:
            """Return a simple message."""
            return "Hello, World!"

        session = requests.Session()
        adapter = req_mock.Adapter()
        session.mount("mock", adapter)

        add_flask_app_to_mock(
            mock_obj=adapter,
            flask_app=app,
            base_url="mock://www.example.com",
        )

        response = session.get("mock://www.example.com")

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"


class TestHTTPretty:
    """
    Tests for using the helper with HTTPretty.

    We only test one way of using the helper with HTTPretty, because the other
    ways also pass in the HTTPretty module.
    """

    @staticmethod
    def test_use() -> None:
        """
        It is possible to use the helper with HTTPretty.
        """
        app = Flask(import_name=__name__, static_folder=None)

        @app.route("/")
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
                "http://www.example.com",
                timeout=_TIMEOUT_SECONDS,
            )

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"
