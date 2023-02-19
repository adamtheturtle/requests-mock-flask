"""
Package for ``requests_mock_flask``.
"""

from __future__ import annotations

import re
from enum import Enum, auto
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import werkzeug
from werkzeug.http import parse_cookie

if TYPE_CHECKING:
    from ._type_check_imports import flask, httpretty, requests, requests_mock


class _MockObjTypes(Enum):
    # A ``requests_mock.Mocker`` or a ``requests_mock.Adapter``.
    REQUESTS_MOCK = auto()
    # A ``responses.RequestsMock``, or the ``responses`` module.
    RESPONSES = auto()
    HTTPRETTY = auto()


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
    # We use hasattr here rather than checking the type of ``mock_obj``.
    #
    # This is so that we do not need to add responses etc. as requirements.
    if hasattr(mock_obj, "add_callback"):
        mock_obj_type = _MockObjTypes.RESPONSES

        def responses_callback(
            request: "requests.PreparedRequest",
        ) -> tuple[int, dict[str, str | int | bool | None], bytes]:
            return _responses_callback(request=request, flask_app=flask_app)

    elif hasattr(mock_obj, "request_history"):
        mock_obj_type = _MockObjTypes.REQUESTS_MOCK

        def requests_mock_callback(
            # We ignore SLF001 here, as we prefer to have this typed with
            # private types than to have it untyped.
            request: "requests_mock.request._RequestObjectProxy",  # noqa: SLF001
            context: "requests_mock.response._Context",  # noqa: SLF001
        ) -> str:
            return _requests_mock_callback(
                request=request,
                context=context,
                flask_app=flask_app,
            )

    elif hasattr(mock_obj, "HTTPretty"):
        mock_obj_type = _MockObjTypes.HTTPRETTY

        def httpretty_callback(
            request: "httpretty.HTTPrettyRequest",
            uri: str,
            headers: dict[str, Any],
        ) -> tuple[int, dict[str, str | int | bool | None], bytes]:
            return _httpretty_callback(
                request=request,
                uri=uri,
                headers=headers,
                flask_app=flask_app,
            )

    else:  # pragma: no cover
        message = (
            "Expected a HTTPretty, ``requests_mock``, or ``responses`` "
            f"object, got {type(mock_obj)}."
        )
        raise TypeError(message)

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
    request_cookies = [
        list(parse_cookie(cookie).items())[0]
        for cookie in cookie_list_no_empty
    ]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name="",
            key=key,
            value=value,
        )

    environ_overrides = {}
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

    result_headers: dict[str, str | int | bool | None] = dict(
        response.headers,
    )
    return (response.status_code, result_headers, bytes(response.data))


def _httpretty_callback(
    request: "httpretty.HTTPrettyRequest",
    uri: str,
    headers: dict[str, Any],
    flask_app: "flask.Flask",
) -> tuple[int, dict[str, str | int | bool | None], bytes]:
    # We make this assertion to satisfy linters.
    # The parameters are given to httpretty callbacks, but we do not use them.
    assert [uri, headers]

    test_client = flask_app.test_client()
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    cookie_string = request.headers.get("Cookie", "")
    cookie_list = cookie_string.split(";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    request_cookies = [
        list(parse_cookie(cookie).items())[0]
        for cookie in cookie_list_no_empty
    ]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name="",
            key=key,
            value=value,
        )

    environ_overrides = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path,
        method=request.method,
        headers=dict(request.headers),
        data=request.body,
        environ_overrides=environ_overrides,
    )
    response = test_client.open(environ_builder.get_request())

    result_headers: dict[str, str | int | bool | None] = dict(
        response.headers,
    )
    return (response.status_code, result_headers, response.data)


def _requests_mock_callback(
    # We ignore SLF001 here, as we prefer to have this typed with
    # private types than to have it untyped.
    request: "requests_mock.request._RequestObjectProxy",  # noqa: SLF001
    context: "requests_mock.response._Context",  # noqa: SLF001
    flask_app: "flask.Flask",
) -> str:
    """
    Given a request to the flask app, send an equivalent request to an in
    memory fake of the flask app and return some key details of the
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
    request_cookies = [
        list(parse_cookie(cookie).items())[0]
        for cookie in cookie_list_no_empty
    ]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name="",
            key=key,
            value=value,
        )

    environ_overrides = {}
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
