"""Package for ``requests_mock_flask``."""

import re
from http.cookies import SimpleCookie
from types import ModuleType
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import httpretty  # pyright: ignore[reportMissingTypeStubs]
import httpx
import requests_mock
import responses
import respx
import werkzeug

if TYPE_CHECKING:
    import flask
    import requests


_MockObjType = (
    responses.RequestsMock
    | requests_mock.Mocker
    | requests_mock.Adapter
    | respx.MockRouter
    | respx.Router
    | ModuleType
)


def add_flask_app_to_mock(
    mock_obj: _MockObjType,
    flask_app: "flask.Flask",
    base_url: str,
) -> None:
    """
    Make it so that requests sent to the ``base_url`` are forwarded to
    the
    ``Flask`` app, when in the context of the ``mock_obj``.
    """
    transport = httpx.WSGITransport(app=flask_app)

    def respx_side_effect(
        request: httpx.Request,
    ) -> httpx.Response:
        """Side effect for respx."""
        return transport.handle_request(request=request)

    def responses_callback(
        request: "requests.PreparedRequest",
    ) -> tuple[int, dict[str, str], bytes]:
        """Callback for responses."""
        return _responses_callback(request=request, flask_app=flask_app)

    def requests_mock_callback(
        request: "requests_mock.Request",
        context: "requests_mock.Context",
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

    for rule in flask_app.url_map.iter_rules():
        # We replace everything inside angle brackets with a regex pattern.
        # For path variables (<path:...>), we use .+ to match any characters
        # including slashes. For all other variable types, we use [^/]+ to
        # match only within a single path segment.
        path_to_match = re.sub(
            pattern="<path:.+?>",
            repl=".+",
            string=rule.rule,
        )
        path_to_match = re.sub(
            pattern="<.+?>",
            repl="[^/]+",
            string=path_to_match,
        )
        pattern = urljoin(base=base_url, url=path_to_match)
        urls = (re.compile(pattern=pattern), re.compile(pattern=pattern + "$"))

        methods = rule.methods or set()
        for method in methods:
            for url in urls:
                if isinstance(mock_obj, responses.RequestsMock) or (
                    isinstance(mock_obj, ModuleType)
                    and mock_obj.__name__ == "responses"
                ):
                    mock_obj.add_callback(
                        method=method,
                        url=url,
                        callback=responses_callback,
                        content_type=None,
                    )
                elif isinstance(
                    mock_obj, (requests_mock.Mocker | requests_mock.Adapter)
                ):
                    mock_obj.register_uri(
                        method=method,
                        url=url,
                        text=requests_mock_callback,
                    )
                elif isinstance(mock_obj, (respx.MockRouter, respx.Router)):
                    mock_obj.route(
                        method=method,
                        url__regex=url.pattern,
                    ).mock(side_effect=respx_side_effect)
                elif mock_obj.__name__ == "httpretty":
                    httpretty.register_uri(  # type: ignore[no-untyped-call]  # pyright: ignore[reportUnknownMemberType]
                        method=method,
                        uri=url,
                        body=httpretty_callback,  # pyright: ignore[reportArgumentType]
                        forcing_headers={"Content-Type": None},
                    )
                else:
                    msg = (
                        "Expected a HTTPretty, ``requests_mock``, "
                        "``respx``, or ``responses`` object, got "
                        f"module '{mock_obj.__name__}'."
                    )
                    raise TypeError(msg)


def _responses_callback(
    request: "requests.PreparedRequest",
    flask_app: "flask.Flask",
) -> tuple[int, dict[str, str], bytes]:
    """Given a request to the flask app, send an equivalent request to an
    in
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
    cookie_dict = dict(request.headers)
    cookie_string = cookie_dict.get("Cookie", "")
    cookie_list = cookie_string.split(sep=";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    simple_cookie: SimpleCookie = SimpleCookie()
    for cookie in cookie_list_no_empty:
        simple_cookie.load(rawdata=cookie)

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
        method=str(object=request.method),
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
    """Given a request to the Flask app, send an equivalent request to an
    in
    memory fake of the Flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param uri: The URI of the request.
    :param headers: The headers of the request.
    :param flask_app: The Flask application to pass requests to.
    :return: A tuple of status code, response headers and response data
        from the flask app.
    """
    # We do this to satisfy linters.
    # The parameters are given to httpretty callbacks, but we do not use them.
    del uri
    del headers

    test_client = flask_app.test_client()
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    cookie_string = request.headers.get(name="Cookie", failobj="")
    cookie_list = cookie_string.split(sep=";")
    cookie_list_no_empty = [item for item in cookie_list if item]
    simple_cookie: SimpleCookie = SimpleCookie()
    for cookie in cookie_list_no_empty:
        simple_cookie.load(rawdata=cookie)

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
        path=str(object=request.path),
        method=request.method,
        headers=request.headers.items(),
        data=request.body,
        environ_overrides=environ_overrides,
    )
    response = test_client.open(environ_builder.get_request())

    return (response.status_code, dict(response.headers), response.data)


def _requests_mock_callback(
    request: "requests_mock.Request",
    context: "requests_mock.Context",
    flask_app: "flask.Flask",
) -> str:
    """Given a request to the Flask app, send an equivalent request to an
    in
    memory fake of the Flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param context: An object containing the collected known data about
        this response.
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
        simple_cookie.load(rawdata=cookie)

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

    context.headers = dict(response.headers)
    context.status_code = response.status_code
    return str(object=response.data.decode())
