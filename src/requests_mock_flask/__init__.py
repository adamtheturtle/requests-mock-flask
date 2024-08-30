"""
Package for ``requests_mock_flask``.
"""

import re
from enum import Enum, auto
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import werkzeug

if TYPE_CHECKING:
    import flask
    import httpretty  # type: ignore[import-untyped]
    import requests
    from requests_mock import request as requests_mock_request
    from requests_mock import response as requests_mock_response


class _MockObjTypes(Enum):
    """The types of mock objects that can be used."""

    # A ``requests_mock.Mocker`` or a ``requests_mock.Adapter``.
    REQUESTS_MOCK = auto()
    # A ``responses.RequestsMock``, or the ``responses`` module.
    RESPONSES = auto()
    HTTPRETTY = auto()


def _get_mock_obj_type(
    # We allow an `Any` type here, as we do not want to add all mocker types
    # as requirements.
    mock_obj: Any,  # noqa: ANN401
) -> _MockObjTypes:
    """
    Get the type of the mock object.
    """
    if hasattr(mock_obj, "add_callback"):
        return _MockObjTypes.RESPONSES
    if hasattr(mock_obj, "request_history"):
        return _MockObjTypes.REQUESTS_MOCK
    if hasattr(mock_obj, "HTTPretty"):
        return _MockObjTypes.HTTPRETTY

    message = (
        "Expected a HTTPretty, ``requests_mock``, or ``responses`` object, "
        f"got {type(mock_obj)}."
    )
    raise TypeError(message)


def add_flask_app_to_mock(
    # We allow an `Any` type here, as we do not want to add all mocker types
    # as requirements.
    mock_obj: Any,  # noqa: ANN401
    flask_app: "flask.Flask",
    base_url: str,
) -> None:
    """
    Make it so that requests sent to the ``base_url`` are forwarded to the
    ``Flask`` app, when in the context of the ``mock_obj``.
    """

    def responses_callback(
        request: "requests.PreparedRequest",
    ) -> tuple[int, dict[str, str | int | bool | None], bytes]:
        """Callback for responses."""
        return _responses_callback(request=request, flask_app=flask_app)

    def requests_mock_callback(
        request: "requests_mock_request.Request",
        context: "requests_mock_response.Context",
    ) -> str:
        """Callback for requests_mock."""
        return _requests_mock_callback(
            request=request,
            context=context,
            flask_app=flask_app,
        )

    def httpretty_callback(
        request: "httpretty.core.HTTPrettyRequest",
        uri: str,
        headers: dict[str, Any],
    ) -> tuple[int, dict[str, str | int | bool | None], bytes]:
        """Callback for HTTPretty."""
        return _httpretty_callback(
            request=request,
            uri=uri,
            headers=headers,
            flask_app=flask_app,
        )

    mock_obj_type = _get_mock_obj_type(mock_obj=mock_obj)

    for rule in flask_app.url_map.iter_rules():
        # We replace everything inside angle brackets with a match for any
        # string of characters of length > 0.
        path_to_match = re.sub(pattern="<.+>", repl=".+", string=rule.rule)
        pattern = urljoin(base_url, path_to_match)
        url = re.compile(pattern)

        assert rule.methods is not None
        for method in rule.methods:
            if mock_obj_type == _MockObjTypes.RESPONSES:
                mock_obj.add_callback(
                    method=method,
                    url=url,
                    callback=responses_callback,
                    content_type=None,
                )
            elif mock_obj_type == _MockObjTypes.REQUESTS_MOCK:
                mock_obj.register_uri(
                    method=method,
                    url=url,
                    text=requests_mock_callback,
                )
            elif mock_obj_type == _MockObjTypes.HTTPRETTY:
                mock_obj.register_uri(
                    method=method,
                    uri=url,
                    body=httpretty_callback,
                    forcing_headers={"Content-Type": None},
                )
            else:  # pragma: no cover
                pass


def _responses_callback(
    request: "requests.PreparedRequest",
    flask_app: "flask.Flask",
) -> tuple[int, dict[str, str | int | bool | None], bytes]:
    """
    Given a request to the flask app, send an equivalent request to an in
    memory fake of the flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param flask_app: The Flask application to pass requests to.
    :return: A tuple of status code, response headers and response data
        from the flask app.
    """
    test_client = flask_app.test_client()
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    cookie_string = request.headers.get("Cookie", "")
    cookie_list = cookie_string.split(";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    simple_cookie: SimpleCookie = SimpleCookie()
    for cookie in cookie_list_no_empty:
        simple_cookie.load(cookie)

    cookies_dict = {k: v.value for k, v in simple_cookie.items()}

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            domain="localhost",
            key=key,
            value=value,
        )

    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]

    headers_dict = dict(request.headers).items()
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path_url,
        method=str(request.method),
        data=request.body,
        headers=headers_dict,
        environ_overrides=environ_overrides,
    )

    response = test_client.open(environ_builder.get_request())

    return (response.status_code, dict(response.headers), bytes(response.data))


def _httpretty_callback(
    request: "httpretty.core.HTTPrettyRequest",
    uri: str,
    headers: dict[str, Any],
    flask_app: "flask.Flask",
) -> tuple[int, dict[str, str | int | bool | None], bytes]:
    """
    Given a request to the Flask app, send an equivalent request to an in
    memory fake of the Flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param uri: The URI of the request.
    :param headers: The headers of the request.
    :param flask_app: The Flask application to pass requests to.
    :return: A tuple of status code, response headers and response data
        from the flask app.
    """
    # We make this assertion to satisfy linters.
    # The parameters are given to httpretty callbacks, but we do not use them.
    assert [uri, headers]

    test_client = flask_app.test_client()
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    cookie_string = request.headers.get("Cookie", "")
    cookie_list = cookie_string.split(";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    simple_cookie: SimpleCookie = SimpleCookie()
    for cookie in cookie_list_no_empty:
        simple_cookie.load(cookie)

    cookies_dict = {k: v.value for k, v in simple_cookie.items()}

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            domain=request.host,
            key=key,
            value=value,
        )

    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]

    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path,
        method=request.method,
        headers=request.headers.items(),
        data=request.body,
        environ_overrides=environ_overrides,
    )
    response = test_client.open(environ_builder.get_request())

    return (response.status_code, dict(response.headers), response.data)


def _requests_mock_callback(
    request: "requests_mock_request.Request",
    context: "requests_mock_response.Context",
    flask_app: "flask.Flask",
) -> str:
    """
    Given a request to the Flask app, send an equivalent request to an in
    memory fake of the Flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param context: An object containing the collected known data about this
        response.
    :param flask_app: The Flask application to pass requests to.
    :return: A tuple of status code, response headers and response data
        from the flask app.
    """
    test_client = flask_app.test_client()
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    cookie_string = request.headers.get("Cookie", "")
    cookie_list = cookie_string.split(";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    simple_cookie: SimpleCookie = SimpleCookie()
    for cookie in cookie_list_no_empty:
        simple_cookie.load(cookie)

    cookies_dict = {k: v.value for k, v in simple_cookie.items()}

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            domain="localhost",
            key=key,
            value=value,
        )

    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path_url,
        method=request.method,
        headers=dict(request.headers),
        data=request.body,
        environ_overrides=environ_overrides,
    )
    response = test_client.open(environ_builder.get_request())

    context.headers = response.headers
    context.status_code = response.status_code
    return str(response.data.decode())
