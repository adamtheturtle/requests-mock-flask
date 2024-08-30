"""
Tests for the ``requests_mock_flask`` package.

Test with a bunch of route types as per:
https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
"""

import json
import uuid
from functools import partial
from typing import Final

import httpretty  # type: ignore[import-untyped]
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


_MockCtxType = (
    partial[responses.RequestsMock]
    | type[requests_mock.Mocker]
    | type[httpretty.httprettized]
)

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

    @app.route("/")
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

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

    @app.route("/")
    def _() -> str:
        """
        Check that the headers includes {"hello": "world"}
        and no Content-Type.
        """
        assert "Content-Type" not in request.headers
        assert request.headers["hello"] == "world"
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/", headers={"hello": "world"})

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com",
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

    @app.route("/")
    def _() -> tuple[Response, int]:
        """Return a simple JSON message."""
        return jsonify({"hello": "world"}), 201

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = 201
    expected_content_type = "application/json"
    expected_json = {"hello": "world"}

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.json == expected_json

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com",
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

    @app.route("/<my_variable>")
    def _(my_variable: str) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/Frasier")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: Frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/Frasier",
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

    @app.route("/<string:my_variable>")
    def _(my_variable: str) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/Frasier")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: Frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/Frasier",
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

    @app.route("/<int:my_variable>")
    def _(my_variable: int) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get("/4")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: 9"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/4",
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

    @app.route("/<float:my_variable>")
    def _(my_variable: float) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get("/4.0")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: 9.0"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/4.0",
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

    @app.route("/<path:my_variable>")
    def _(my_variable: str) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + my_variable

    test_client = app.test_client()
    response = test_client.get("/foo/bar")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: foo/bar"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/foo/bar",
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

    @app.route("/<string:my_variable>")
    def _(_: str) -> str:
        """Return an empty string."""
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get("/foo/bar")

    expected_status_code = 404
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not found on the server" in response.data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/foo/bar",
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

    @app.route("/<uuid:my_variable>")
    def _(my_variable: uuid.UUID) -> str:
        """Return a simple message which includes the route variables."""
        return "Hello: " + my_variable.hex

    test_client = app.test_client()
    random_uuid = uuid.uuid4()
    response = test_client.get(f"/{random_uuid}")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = f"Hello: {random_uuid.hex}".encode()

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            f"http://www.example.com/{random_uuid}",
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

    @app.route("/users/<int:my_variable>/posts")
    def _(my_variable: int) -> str:
        """Return a simple message which includes the route variable."""
        return "Posts for: " + str(my_variable)

    test_client = app.test_client()
    response = test_client.get("/users/4/posts")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Posts for: 4"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/users/4/posts",
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

    @app.route("/users/<string:my_org>/<string:my_user>/posts")
    def _(my_org: str, my_user: str) -> str:
        """Return a simple message which includes the route variables."""
        return "Posts for: " + my_org + "/" + my_user

    test_client = app.test_client()
    response = test_client.get("/users/cranes/frasier/posts")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Posts for: cranes/frasier"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/users/cranes/frasier/posts",
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

    @app.route("/", methods=["POST"])
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.post("/")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.post(
            "http://www.example.com/",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert mock_response.text == expected_data.decode()


@pytest.mark.parametrize("custom_content_length", ["1", "100"])
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

    @app.route("/", methods=["POST"])
    def _() -> str:
        """Check some features of the request."""
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

    expected_status_code = 200

    assert response.status_code == expected_status_code

    requests_request = requests.Request(
        method="POST",
        url="http://www.example.com/",
        data=data,
    ).prepare()
    requests_request.headers["Content-Length"] = custom_content_length

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

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

    @app.route("/", methods=["GET", "POST"])
    def _() -> str:
        """Return a simple message."""
        return "Hello, World!"

    test_client = app.test_client()
    get_response = test_client.get("/")
    post_response = test_client.post("/")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert get_response.status_code == expected_status_code
    assert get_response.headers["Content-Type"] == expected_content_type
    assert get_response.data == expected_data

    assert post_response.status_code == expected_status_code
    assert post_response.headers["Content-Type"] == expected_content_type
    assert post_response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_get_response = requests.get(
            "http://www.example.com/",
            timeout=_TIMEOUT_SECONDS,
        )
        mock_post_response = requests.post(
            "http://www.example.com/",
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

    @app.route("/<int:my_variable>")
    def _(_: int) -> str:
        """Return an empty string."""
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get("/a")

    expected_status_code = 404
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not found on the server" in response.data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/a",
            timeout=_TIMEOUT_SECONDS,
        )

    assert mock_response.status_code == expected_status_code
    assert mock_response.headers["Content-Type"] == expected_content_type
    assert "not found on the server" in mock_response.text


@_MOCK_CTX_MARKER
def test_404_no_such_method(mock_ctx: _MockCtxType) -> None:
    """
    A route with the wrong method given works.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route("/")
    def _() -> str:
        """Return an empty string."""
        return ""  # pragma: no cover

    test_client = app.test_client()
    response = test_client.post("/")

    expected_status_code = 405
    expected_content_type = "text/html; charset=utf-8"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert b"not allowed for the requested URL." in response.data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        with pytest.raises(
            expected_exception=(
                requests.exceptions.ConnectionError,
                NoMockAddress,
                ValueError,
            ),
        ):
            requests.post("http://www.example.com/", timeout=_TIMEOUT_SECONDS)


@_MOCK_CTX_MARKER
def test_request_needs_content_type(mock_ctx: _MockCtxType) -> None:
    """
    Routes which require a content type are supported.
    """
    app = Flask(import_name=__name__, static_folder=None)

    @app.route("/")
    def _() -> str:
        """Check the MIME type and return a simple message."""
        assert request.mimetype == "application/json"
        return "Hello, World!"

    test_client = app.test_client()
    response = test_client.get("/", content_type="application/json")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com",
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

    @app.route("/")
    def _() -> str:
        """Check the MIME type and return some given data."""
        assert request.mimetype == "application/json"
        request_json = request.get_json()
        return str(request_json["hello"])

    test_client = app.test_client()
    response = test_client.get(
        "/",
        content_type="application/json",
        data=json.dumps({"hello": "world"}),
    )

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"world"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"hello": "world"}),
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
        """Return a string which includes the type of the variable."""
        return f"{variable}, {type(variable)}"

    app.add_url_rule(rule="/<variable>", view_func=show_type)
    app.add_url_rule(rule="/<int:variable>", view_func=show_type)
    app.add_url_rule(rule="/<string:variable>", view_func=show_type)

    test_client = app.test_client()
    response = test_client.get("/4")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"4, <class 'int'>"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com/4",
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

    @app.route("/")
    def _() -> str:
        """Return a simple message which includes a request query parameter."""
        result = request.args["frasier"]
        return "Hello: " + str(result)

    test_client = app.test_client()
    response = test_client.get("/?frasier=crane")

    expected_status_code = 200
    expected_content_type = "text/html; charset=utf-8"
    expected_data = b"Hello: crane"

    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"] == expected_content_type
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.get(
            "http://www.example.com?frasier=crane",
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

    @app.route("/", methods=["POST"])
    def _() -> Response:
        """Set cookies and return a simple message."""
        response = make_response()
        response.set_cookie("frasier_set", "crane_set")
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

    expected_status_code = 200
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
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response = requests.post(
            "http://www.example.com",
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

    @app.route("/", methods=["GET"])
    def _() -> Response:
        """Return a simple message with no Content-Type."""
        response = make_response()
        response.data = "Hello, World!"
        del response.headers["Content-Type"]
        return response

    test_client = app.test_client()
    response = test_client.get("/")

    expected_status_code = 200
    expected_data = b"Hello, World!"

    assert response.status_code == expected_status_code
    assert "Content-Type" not in response.headers
    assert response.data == expected_data

    with mock_ctx() as mock_obj:
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

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
        """Return a simple message."""
        return "Hello: World"

    def with_variable(my_variable: str) -> str:
        """Return a simple message which includes the route variable."""
        return "Hello: " + my_variable

    app.add_url_rule(rule="/base", methods=["GET"], view_func=base_route)
    app.add_url_rule(
        rule="/base/<string:my_variable>",
        methods=["GET"],
        view_func=with_variable,
    )

    test_client = app.test_client()
    response = test_client.get("/base")

    expected_status_code = 200
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
        if mock_ctx == httpretty.httprettized:
            mock_obj_to_add = httpretty
        else:
            mock_obj_to_add = mock_obj

        add_flask_app_to_mock(
            mock_obj=mock_obj_to_add,
            flask_app=app,
            base_url="http://www.example.com",
        )

        mock_response_base = requests.get(
            "http://www.example.com/base",
            timeout=_TIMEOUT_SECONDS,
        )

        mock_response_var = requests.get(
            "http://www.example.com/base/Frasier",
            timeout=_TIMEOUT_SECONDS,
        )

        mock_response_base_2 = requests.get(
            "http://www.example.com/base",
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


def test_unknown_mock_type() -> None:
    """
    When an unknown mock type is passed in, an error is raised.
    """
    expected_error = (
        "Expected a HTTPretty, ``requests_mock``, or ``responses`` object, "
        "got <class 'object'>."
    )
    with pytest.raises(expected_exception=TypeError, match=expected_error):
        add_flask_app_to_mock(
            mock_obj=object(),
            flask_app=Flask(import_name=__name__, static_folder=None),
            base_url="http://www.example.com",
        )
