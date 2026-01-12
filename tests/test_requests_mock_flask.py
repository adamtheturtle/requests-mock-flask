"""Tests for the ``requests_mock_flask`` package.

Test with a bunch of route types as per:
https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
"""

import json
import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from functools import partial
from http import HTTPStatus
from types import ModuleType
from typing import Final

import httpretty  # pyright: ignore[reportMissingTypeStubs]
import pytest
import requests
import requests_mock
import responses
import werkzeug
from flask import Flask, Response, jsonify, make_response, request
from requests_mock.exceptions import NoMockAddress

from requests_mock_flask import add_flask_app_to_mock

# We use a high timeout to allow interactive debugging while requests are being
# made.
_TIMEOUT_SECONDS: Final[int] = 120

_MockObjType = responses.RequestsMock | requests_mock.Mocker | ModuleType
_MockCtxManagerYieldType = _MockObjType | None
_MockCtxType = Callable[[], AbstractContextManager[_MockCtxManagerYieldType]]

_MOCK_CTXS: list[_MockCtxType] = [
    partial(responses.RequestsMock, assert_all_requests_are_fired=False),
    requests_mock.Mocker,
    httpretty.httprettized,
]

_MOCK_IDS = ["responses", "requests_mock", "httpretty"]

_MOCK_CTX_MARKER = pytest.mark.parametrize(
    argnames="mock_ctx",
    argvalues=_MOCK_CTXS,
    ids=_MOCK_IDS,
)


@_MOCK_CTX_MARKER
def test_simple_route(mock_ctx: _MockCtxType) -> None:
    """
    A simple GET route works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Return a simple message.
        """
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_headers(mock_ctx: _MockCtxType) -> None:
    """
    Request headers are sent.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Check that the headers includes {"hello": "world"} and no Content-Type.
        """
        assert "Content-Type" not in request.headers
        assert request.headers["hello"] == "world"
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/", headers={"hello": "world"})

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            headers={"hello": "world"},
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_json(mock_ctx: _MockCtxType) -> None:
    """
    A route that returns JSON data works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> tuple[Response, int]:
        """
        Return a simple JSON message.
        """
        return jsonify({"hello": "world"}), HTTPStatus.CREATED

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = HTTPStatus.CREATED
    expected_content_type = "application/json"
    expected_json = {"hello": "world"}

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.json == expected_json

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.json() == expected_json


@_MOCK_CTX_MARKER
def test_route_with_variable_no_type_given(mock_ctx: _MockCtxType) -> None:
    """
    A route with a variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<my_variable>")
    def _(my_variable: str) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/Frasier")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: Frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/Frasier",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_string_variable(mock_ctx: _MockCtxType) -> None:
    """
    A route with a string variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<string:my_variable>")
    def _(my_variable: str) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/Frasier")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: Frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/Frasier",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_int_variable(mock_ctx: _MockCtxType) -> None:
    """
    A route with an int variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<int:my_variable>")
    def _(my_variable: int) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return f"Hello: {my_variable + 5}"

    test_client = app.test_client()
    response = test_client.get("/4")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: 9"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/4",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_float_variable(mock_ctx: _MockCtxType) -> None:
    """
    A route with a float variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<float:my_variable>")
    def _(my_variable: float) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return f"Hello: {my_variable + 5}"

    test_client = app.test_client()
    response = test_client.get("/4.0")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: 9.0"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/4.0",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_path_variable_with_slash(mock_ctx: _MockCtxType) -> None:
    """
    A route with a path variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<path:my_variable>")
    def _(my_variable: str) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/foo/bar")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: foo/bar"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/foo/bar",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_string_variable_with_slash(mock_ctx: _MockCtxType) -> None:
    """
    A route with a string variable when given a slash works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<string:my_variable>")
    def _(_: str) -> str:
        """
        Return an empty string.
        """
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get("/foo/bar")

    expected_status_code = HTTPStatus.NOT_FOUND
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not found on the server" in response.data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/foo/bar",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert "not found on the server" in mock_response.text


@_MOCK_CTX_MARKER
def test_route_with_uuid_variable(mock_ctx: _MockCtxType) -> None:
    """
    A route with a uuid variable works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<uuid:my_variable>")
    def _(my_variable: uuid.UUID) -> str:
        """
        Return a simple message which includes the route variables.
        """
        return "Hello: " + my_variable.hex

    test_client = app.test_client()
    random_uuid = uuid.uuid4()
    response = test_client.get(f"/{random_uuid}")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = f"Hello: {random_uuid.hex}".encode()

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url=f"http://www.example.com/{random_uuid}",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_nested_path(mock_ctx: _MockCtxType) -> None:
    """
    A route with a variable nested in a path works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/users/<int:my_variable>/posts")
    def _(my_variable: int) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return f"Posts for: {my_variable}"

    test_client = app.test_client()
    response = test_client.get("/users/4/posts")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Posts for: 4"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/users/4/posts",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_route_with_multiple_variables(mock_ctx: _MockCtxType) -> None:
    """
    A route with multiple variables works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/users/<string:my_org>/<string:my_user>/posts")
    def _(my_org: str, my_user: str) -> str:
        """
        Return a simple message which includes the route variables.
        """
        return "Posts for: " + my_org + "/" + my_user

    test_client = app.test_client()
    response = test_client.get("/users/cranes/frasier/posts")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Posts for: cranes/frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/users/cranes/frasier/posts",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_post_verb(mock_ctx: _MockCtxType) -> None:
    """
    A route with the POST verb works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/", methods=["POST"])
    def _() -> str:
        """
        Return a simple message.
        """
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.post("/")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.post(
            url="http://www.example.com/",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@pytest.mark.parametrize(
    argnames="custom_content_length",
    argvalues=["1", "100"],
)
@_MOCK_CTX_MARKER
def test_incorrect_content_length(
    custom_content_length: str,
    mock_ctx: _MockCtxType,
) -> None:
    """
    Custom content length headers are passed through to the Flask endpoint.
    """
    app = Flask(import_name=__name__, static_folder=None)
    data = b"12345"

    @app.route(rule="/", methods=["POST"])
    def _() -> str:
        """
        Check some features of the request.
        """
        request.environ["wsgi.input_terminated"] = True
        assert len(data) == len(request.data)
        assert request.headers["Content-Length"] == custom_content_length
        return ""

    test_client = app.test_client()
    environ_builder = werkzeug.test.EnvironBuilder(
        path="/",
        method="POST",
        data=b"12345",
        environ_overrides={"CONTENT_LENGTH": custom_content_length},
    )

    response = test_client.open(environ_builder.get_request())

    expected_status_code = HTTPStatus.OK

    assert response.status_code == expected_status_code

    requests_request = requests.Request(
        method="POST",
        url="http://www.example.com/",
        data=data,
    ).prepare()
    requests_request.headers["Content-Length"] = custom_content_length

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        session = requests.Session()
        mock_response = session.send(request=requests_request)

    assert mock_response.status_code == expected_status_code


@_MOCK_CTX_MARKER
def test_multiple_http_verbs(mock_ctx: _MockCtxType) -> None:
    """
    A route with multiple verbs works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/", methods=["GET", "POST"])
    def _() -> str:
        """
        Return a simple message.
        """
        return "Hello, World!"

    test_client = app.test_client()
    get_response = test_client.get("/")
    post_response = test_client.post("/")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert get_response.status_code == expected_status_code
    assert get_response.headers["Content-Type"] == expected_content_type
    assert get_response.data == expected_data

    assert post_response.status_code == expected_status_code
    assert post_response.headers["Content-Type"] == expected_content_type
    assert post_response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_get_response = requests.get(
            url="http://www.example.com/",
            timeout=_TIMEOUT_SECONDS,
        )
        mock_post_response = requests.post(
            url="http://www.example.com/",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_get_response.status_code == expected_status_code
    assert mock_get_response.headers["Content-Type"] == expected_content_type
    assert mock_get_response.text == expected_data.decode()

    assert mock_post_response.status_code == expected_status_code
    assert mock_post_response.headers["Content-Type"] == expected_content_type
    assert mock_post_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_wrong_type_given(mock_ctx: _MockCtxType) -> None:
    """
    A route with the wrong type given works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/<int:my_variable>")
    def _(_: int) -> str:
        """
        Return an empty string.
        """
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get("/a")

    expected_status_code = HTTPStatus.NOT_FOUND
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not found on the server" in response.data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/a",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert "not found on the server" in mock_response.text


@_MOCK_CTX_MARKER
def test_405_no_such_method(mock_ctx: _MockCtxType) -> None:
    """
    A route with the wrong method given works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Return an empty string.
        """
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.post("/")

    expected_status_code = HTTPStatus.METHOD_NOT_ALLOWED
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not allowed for the requested URL." in response.data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        expected_exceptions: tuple[type[Exception], ...] = (
            requests.exceptions.ConnectionError,
            NoMockAddress,
            ValueError,
        )
        with pytest.raises(expected_exception=expected_exceptions):
            requests.post(
                url="http://www.example.com/",
                timeout=_TIMEOUT_SECONDS,
            )


@_MOCK_CTX_MARKER
def test_request_needs_content_type(mock_ctx: _MockCtxType) -> None:
    """
    Routes which require a content type are supported.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Check the MIME type and return a simple message.
        """
        assert request.mimetype == "application/json"
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/", content_type="application/json")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_request_needs_data(mock_ctx: _MockCtxType) -> None:
    """
    Routes which require data are supported.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Check the MIME type and return some given data.
        """
        assert request.mimetype == "application/json"
        request_json = request.get_json()
        return str(object=request_json["hello"])

    test_client = app.test_client()
    response = test_client.get(
        "/",
        content_type="application/json",
        data=json.dumps(obj={"hello": "world"}),
    )

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"world"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            headers={"Content-Type": "application/json"},
            data=json.dumps(obj={"hello": "world"}),
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_multiple_functions_same_path_different_type(
    mock_ctx: _MockCtxType,
) -> None:
    """
    When multiple functions exist with the same path but have a different type,
    the mock matches them just the same.
    """
    app = Flask(import_name=__name__, static_folder=None)

    def show_type(variable: float | str) -> str:
        """
        Return a string which includes the type of the variable.
        """
        return f"{variable}, {type(variable)}"

    app.add_url_rule(rule="/<variable>", view_func=show_type)
    app.add_url_rule(rule="/<int:variable>", view_func=show_type)
    app.add_url_rule(rule="/<string:variable>", view_func=show_type)

    test_client = app.test_client()
    response = test_client.get("/4")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"4, <class 'int'>"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com/4",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_query_string(mock_ctx: _MockCtxType) -> None:
    """
    Query strings work.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Return a simple message which includes a request query parameter.
        """
        result = request.args["frasier"]
        return f"Hello: {result}"

    test_client = app.test_client()
    response = test_client.get("/?frasier=crane")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: crane"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com?frasier=crane",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_cookies(mock_ctx: _MockCtxType) -> None:
    """
    Cookies work.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/", methods=["POST"])
    def _() -> Response:
        """
        Set cookies and return a simple message.
        """
        response = make_response()
        response.set_cookie(key="frasier_set", value="crane_set")
        assert request.cookies, request
        assert request.cookies["frasier"] == "crane"
        assert request.cookies["frasier2"] == "crane2"
        response.data = "Hello, World!"
        return response

    test_client = app.test_client()
    test_client.set_cookie(
        domain="localhost",
        key="frasier",
        value="crane",
    )
    test_client.set_cookie(
        domain="localhost",
        key="frasier2",
        value="crane2",
    )
    response = test_client.post("/")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code, response.data
    assert response.headers["Content-Type"] == expected_content_type
    new_cookie = test_client.get_cookie(key="frasier_set")
    assert new_cookie is not None
    assert new_cookie.key == "frasier_set"
    assert new_cookie.value == "crane_set"
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.post(
            url="http://www.example.com",
            cookies={
                "frasier": "crane",
                "frasier2": "crane2",
            },
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()
    assert mock_response.cookies["frasier_set"] == "crane_set"


@_MOCK_CTX_MARKER
def test_no_content_type(mock_ctx: _MockCtxType) -> None:
    """
    It is possible to get a response without a content type.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/", methods=["GET"])
    def _() -> Response:
        """
        Return a simple message with no Content-Type.
        """
        response = make_response()
        response.data = "Hello, World!"
        del response.headers["Content-Type"]
        return response

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = HTTPStatus.OK
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert "Content-Type" not in response.headers
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            url="http://www.example.com",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert "Content-Type" not in mock_response.headers
    assert mock_response.text == expected_data.decode()


@_MOCK_CTX_MARKER
def test_overlapping_routes_multiple_requests(mock_ctx: _MockCtxType) -> None:
    """
    A route with overlap to another route works across multiple requests.
    """
    app = Flask(import_name=__name__, static_folder=None)

    def base_route() -> str:
        """
        Return a simple message.
        """
        return "Hello: World"

    def with_variable(my_variable: str) -> str:
        """
        Return a simple message which includes the route variable.
        """
        return "Hello: " + my_variable

    app.add_url_rule(rule="/base", methods=["GET"], view_func=base_route)
    app.add_url_rule(
        rule="/base/<string:my_variable>",
        methods=["GET"],
        view_func=with_variable,
    )

    test_client = app.test_client()
    response = test_client.get("/base")

    expected_status_code = HTTPStatus.OK
    expected_content_type = "text/html; charset=utf-8"
    expected_base_data = b"Hello: World"

    assert response.status_code == expected_status_code
    assert response.data == expected_base_data

    test_client = app.test_client()
    response = test_client.get("/base/Frasier")

    expected_var_data = b"Hello: Frasier"

    assert response.status_code == expected_status_code
    assert response.data == expected_var_data

    with mock_ctx() as mock_obj:
        mock_obj_to_add = mock_obj or httpretty

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response_base = requests.get(
            url="http://www.example.com/base",
            timeout=_TIMEOUT_SECONDS,
        )

        mock_response_var = requests.get(
            url="http://www.example.com/base/Frasier",
            timeout=_TIMEOUT_SECONDS,
        )

        mock_response_base_2 = requests.get(
            url="http://www.example.com/base",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response_base.status_code == expected_status_code
    assert mock_response_base.headers["Content-Type"] == expected_content_type
    assert mock_response_base.text == expected_base_data.decode()

    assert mock_response_var.status_code == expected_status_code
    assert mock_response_var.headers["Content-Type"] == expected_content_type
    assert mock_response_var.text == expected_var_data.decode()

    assert mock_response_base_2.status_code == expected_status_code
    assert (
        mock_response_base_2.headers["Content-Type"] == expected_content_type
    )
    assert mock_response_base_2.text == expected_base_data.decode()


_MOCK_CTXS_NO_HTTPRETTY: list[_MockCtxType] = [
    partial(responses.RequestsMock, assert_all_requests_are_fired=False),
    requests_mock.Mocker,
]

_MOCK_IDS_NO_HTTPRETTY = ["responses", "requests_mock"]

_MOCK_CTX_MARKER_NO_HTTPRETTY = pytest.mark.parametrize(
    argnames="mock_ctx",
    argvalues=_MOCK_CTXS_NO_HTTPRETTY,
    ids=_MOCK_IDS_NO_HTTPRETTY,
)


@_MOCK_CTX_MARKER_NO_HTTPRETTY
def test_multiple_variables_no_extra_segments(mock_ctx: _MockCtxType) -> None:
    """A route with multiple variables should not match URLs with extra
    segments.

    This is a regression test for
    https://github.com/adamtheturtle/requests-mock-flask/issues/1540.

    The bug was that the regex pattern `<.+>` was greedy, so it would match
    from the first `<` to the last `>`, collapsing multiple variables into a
    single wildcard. For example, `/users/<org>/<user>/posts` would become
    `/users/.+/posts` instead of `/users/.+/.+/posts`.

    This caused URLs with extra segments like `/users/myorg/myuser/extra/posts`
    to incorrectly match the route.

    Note: This test excludes httpretty because httpretty allows real network
    connections for unmatched URLs by default, and there's no way to configure
    this when using the httprettized decorator.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/users/<string:my_org>/<string:my_user>/posts")
    def _(my_org: str, my_user: str) -> str:
        """
        Return a simple message which includes the route variables.
        """
        return "Posts for: " + my_org + "/" + my_user

    # Verify the real Flask app rejects URLs with extra segments
    test_client = app.test_client()
    response = test_client.get("/users/cranes/frasier/extra/posts")
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Verify the mock also rejects URLs with extra segments
    with mock_ctx() as mock_obj:
        add_flask_app_to_mock(
            mock_obj=mock_obj,
            flask_app=app,
            base_url="http://www.example.com",
        )

        # Verify that the correct URL still works
        valid_response = requests.get(
            url="http://www.example.com/users/cranes/frasier/posts",
            timeout=_TIMEOUT_SECONDS,
        )
        assert valid_response.status_code == HTTPStatus.OK
        assert valid_response.text == "Posts for: cranes/frasier"

        # Verify that URLs with extra segments are rejected
        expected_exceptions: tuple[type[Exception], ...] = (
            requests.exceptions.ConnectionError,
            NoMockAddress,
        )
        with pytest.raises(expected_exception=expected_exceptions):
            requests.get(
                url="http://www.example.com/users/cranes/frasier/extra/posts",
                timeout=_TIMEOUT_SECONDS,
            )


def test_unknown_mock_module() -> None:
    """
    When an unknown mock module is passed in, an error is raised.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route(rule="/")
    def _() -> str:
        """
        Return a simple message.
        """
        return ""  # pragma: no cover

    expected_error = (
        "Expected a HTTPretty, ``requests_mock``, or ``responses`` object, "
        "got module 'json'."
    )
    with pytest.raises(expected_exception=TypeError, match=expected_error):
        add_flask_app_to_mock(
            mock_obj=json,
            flask_app=app,
            base_url="http://www.example.com",
        )
