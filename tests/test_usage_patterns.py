"""
Tests for ways the helper can be used.
"""

from http import HTTPStatus

import httpretty
import requests
import requests_mock
import responses
from flask import Flask
from requests_mock_flask import add_flask_app_to_mock


class TestResponses:
    """
    Tests for using the helper with ``responses``.
    """

    @staticmethod
    def test_context_manager() -> None:
        """
        It is possible to use the helper with a ``responses`` context manager.
        """
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        with responses.RequestsMock(
            assert_all_requests_are_fired=False,
        ) as resp_m:
            add_flask_app_to_mock(
                mock_obj=resp_m,
                flask_app=app,
                base_url="http://www.example.com",
            )

            response = requests.get("http://www.example.com", timeout=1)

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"

    @staticmethod
    @responses.activate
    def test_decorator() -> None:
        """
        It is possible to use the helper with a ``responses`` decorator.
        """
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        add_flask_app_to_mock(
            mock_obj=responses,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = requests.get("http://www.example.com", timeout=1)

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
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        with requests_mock.Mocker() as resp_m:
            add_flask_app_to_mock(
                mock_obj=resp_m,
                flask_app=app,
                base_url="http://www.example.com",
            )

            response = requests.get("http://www.example.com", timeout=1)

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"

    @staticmethod
    def test_fixture(  # pylint: disable=redefined-outer-name
        requests_mock: requests_mock.Mocker,
    ) -> None:
        """
        It is possible to use the helper with a ``requests_mock`` fixture.
        """
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        add_flask_app_to_mock(
            mock_obj=requests_mock,
            flask_app=app,
            base_url="http://www.example.com",
        )

        response = requests.get("http://www.example.com", timeout=1)

        assert response.status_code == HTTPStatus.OK

    @staticmethod
    def test_adapter() -> None:
        """
        It is possible to use the helper with a ``requests_mock`` adapter.
        """
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        session = requests.Session()
        adapter = requests_mock.Adapter()
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
        app = Flask(__name__)

        @app.route("/")
        def _() -> str:
            return "Hello, World!"

        with httpretty.enabled():
            add_flask_app_to_mock(
                mock_obj=httpretty,
                flask_app=app,
                base_url="http://www.example.com",
            )

            response = requests.get("http://www.example.com", timeout=1)

        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello, World!"
