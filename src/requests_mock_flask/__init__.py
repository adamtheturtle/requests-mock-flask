"""Package for ``requests_mock_flask``."""

from __future__ import annotations

import dataclasses
import re
from operator import methodcaller
from types import ModuleType
from typing import TYPE_CHECKING, Any, BinaryIO
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

import httpretty
import httpx
import requests_mock
import responses
import respx
import werkzeug
from urllib3 import HTTPHeaderDict

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from wsgiref.types import StartResponse, WSGIEnvironment

    import flask
    import requests
    from werkzeug.routing import Rule

    type _RequestBody = (
        str
        | bytes
        | bytearray
        | memoryview
        | Iterable[str | bytes]
        | BinaryIO
        | None
    )


def _without_transfer_encoding(
    headers: Iterable[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Return headers excluding ``Transfer-Encoding``."""
    return [
        (key, value)
        for key, value in headers
        if key.lower() != "transfer-encoding"
    ]


def _is_binary_io(body: object) -> bool:
    """Return whether the body provides a file-like ``read`` method."""
    return any("read" in vars(cls) for cls in type(body).mro())


def _normalize_body(
    body: _RequestBody,
) -> str | bytes | None:
    """Convert streaming request bodies to bytes for the WSGI app."""
    if body is None or isinstance(body, str | bytes):
        return body
    if isinstance(body, bytearray | memoryview):
        return bytes(body)
    if _is_binary_io(body=body):
        body_bytes: bytes = methodcaller("read")(body)
        return body_bytes
    return b"".join(
        part.encode() if isinstance(part, str) else part for part in body
    )


# Known HTTP methods to register for every route URL. We register all of
# these (rather than only the methods a rule supports) so that requests using
# an unsupported method for a known path are still forwarded to Flask, which
# then returns its usual ``405 Method Not Allowed`` response (including the
# ``Allow`` header and any custom error handler).
_KNOWN_HTTP_METHODS = frozenset(
    {
        "GET",
        "HEAD",
        "OPTIONS",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "TRACE",
    },
)


_MockObjType = (
    responses.RequestsMock
    | requests_mock.Mocker
    | requests_mock.Adapter
    | respx.MockRouter
    | respx.Router
    | ModuleType
)


def _host_rule_matches_base_url(
    *,
    rule: Rule,
    base_url_host: str | None,
) -> bool:
    """Return whether a Flask host rule applies to ``base_url_host``."""
    if base_url_host is None:
        return False

    rule.compile()
    host_parts: list[str] = []
    rule_attributes: Any = vars(rule)
    rule_trace = rule_attributes["_trace"]
    rule_converters = rule_attributes["_converters"]
    separator_index = rule_trace.index((False, "|"))
    for is_dynamic, data in rule_trace[:separator_index]:
        if is_dynamic:
            converter = rule_converters[data]
            host_parts.append(f"(?:{converter.regex})")
        else:
            host_parts.append(re.escape(pattern=_host_to_idna(host=data)))

    host_pattern = "".join(host_parts)
    return re.fullmatch(pattern=host_pattern, string=base_url_host) is not None


@dataclasses.dataclass(frozen=True)
class _MockCallbacks:
    """Callbacks for each supported mock back end."""

    responses: Callable[..., Any]
    requests_mock: Callable[..., Any]
    respx: Callable[..., Any]
    httpretty: Callable[..., Any]


def _register_mock(
    mock_obj: _MockObjType,
    method: str,
    url: re.Pattern[str],
    callbacks: _MockCallbacks,
) -> None:
    """Register a single method/URL pair with the given mock back end.

    To support a new mock back end, add a case branch.
    """
    match mock_obj:
        case responses.RequestsMock() | ModuleType() if (
            not isinstance(mock_obj, ModuleType)
            or mock_obj.__name__ == "responses"
        ):
            mock_obj.add_callback(
                method=method,
                url=url,
                callback=callbacks.responses,
                content_type=None,
            )
        case requests_mock.Mocker() | requests_mock.Adapter():
            mock_obj.register_uri(
                method=method,
                url=url,
                content=callbacks.requests_mock,
            )
        case respx.MockRouter() | respx.Router():
            mock_obj.route(
                method=method,
                url__regex=url.pattern,
            ).mock(side_effect=callbacks.respx)
        case ModuleType() if mock_obj.__name__ == "httpretty":
            httpretty.register_uri(
                method=method,
                uri=url,
                body=callbacks.httpretty,
                forcing_headers={"Content-Type": None},
            )
        case _:
            if isinstance(mock_obj, ModuleType):
                name = mock_obj.__name__
            else:
                name = type(mock_obj).__name__
            msg = (
                "Expected a HTTPretty, ``requests_mock``, "
                "``respx``, or ``responses`` object, got "
                f"module '{name}'."
            )
            raise TypeError(msg)


def _normalize_base_url(*, base_url: str) -> str:
    """Lowercase the case-insensitive scheme and host of ``base_url``.

    HTTP clients normalize the scheme and host to lowercase before matching
    requests, so a ``base_url`` with uppercase scheme or host characters
    would otherwise register patterns that no client can reach. The user
    information, path and query components retain their original case.
    """
    parts = urlsplit(url=base_url)
    userinfo, separator, hostport = parts.netloc.rpartition("@")
    netloc = userinfo + separator + hostport.lower()
    return urlunsplit(
        components=(
            parts.scheme.lower(),
            netloc,
            parts.path,
            parts.query,
            parts.fragment,
        )
    )


def _host_to_idna(*, host: str) -> str:
    """Return an internationalized host in ASCII IDNA form."""
    if host.isascii() or ":" in host:
        return host
    return ".".join(
        label.encode(encoding="idna").decode(encoding="ascii") if label else ""
        for label in host.split(sep=".")
    )


def _normalize_base_url_host_to_idna(*, base_url: str) -> str:
    """
    Return ``base_url`` with any internationalized host encoded using
    IDNA.

    HTTP clients convert Unicode host names to their ASCII IDNA form
    before sending a request, so the registered pattern must use the same
    ASCII form in order to intercept those requests.
    """
    split = urlsplit(url=base_url)
    host = split.hostname
    if host is None:
        return base_url
    idna_host = _host_to_idna(host=host)
    if idna_host == host:
        return base_url

    userinfo, separator, hostport = split.netloc.rpartition("@")
    _, port_separator, port = hostport.partition(":")
    normalized_hostport = idna_host + port_separator + port
    normalized_netloc = userinfo + separator + normalized_hostport
    prefix, _, suffix = base_url.partition(split.netloc)
    return prefix + normalized_netloc + suffix


def add_flask_app_to_mock(
    mock_obj: _MockObjType,
    flask_app: flask.Flask,
    base_url: str,
) -> None:
    """
    Make it so that requests sent to the ``base_url`` are forwarded to
    the
    ``Flask`` app, when in the context of the ``mock_obj``.
    """
    base_url = _normalize_base_url(base_url=base_url)
    base_url = _normalize_base_url_host_to_idna(base_url=base_url)

    def respx_wsgi_app(
        environ: WSGIEnvironment,
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        """Normalize HTTPX's Unicode path to the WSGI latin-1
        convention.
        """
        path_info = environ["PATH_INFO"]
        environ["PATH_INFO"] = path_info.encode().decode("latin-1")
        return flask_app.wsgi_app(
            environ=environ,
            start_response=start_response,
        )

    transport = httpx.WSGITransport(app=respx_wsgi_app)

    def respx_side_effect(
        request: httpx.Request,
    ) -> httpx.Response:
        """Side effect for respx."""
        return transport.handle_request(request=request)

    def responses_callback(
        request: requests.PreparedRequest,
    ) -> tuple[int, HTTPHeaderDict, bytes]:
        """Callback for responses."""
        return _responses_callback(request=request, flask_app=flask_app)

    def requests_mock_callback(
        request: requests_mock.Request,
        context: requests_mock.Context,
    ) -> bytes:
        """Callback for requests_mock."""
        return _requests_mock_callback(
            request=request,
            context=context,
            flask_app=flask_app,
        )

    def httpretty_callback(
        request: httpretty.core.HTTPrettyRequest,
        uri: str,
        headers: dict[str, Any],
    ) -> tuple[int, HTTPHeaderDict, bytes]:
        """Callback for HTTPretty."""
        return _httpretty_callback(
            request=request,
            uri=uri,
            headers=headers,
            flask_app=flask_app,
        )

    callbacks = _MockCallbacks(
        responses=responses_callback,
        requests_mock=requests_mock_callback,
        respx=respx_side_effect,
        httpretty=httpretty_callback,
    )

    base_url_host = urlsplit(url=base_url).hostname
    for rule in flask_app.url_map.iter_rules():
        if rule.host is not None and not _host_rule_matches_base_url(
            rule=rule,
            base_url_host=base_url_host,
        ):
            continue
        # Build the URL pattern from the framework's parsed rule metadata.
        # Re-parsing ``rule.rule`` with a naive regex breaks on
        # converter arguments that contain a quoted ``>`` (e.g.
        # ``<regex("[^>]+"):value>``). ``rule.compile()`` populates
        # internal parsed parts and each variable's converter.
        #
        # For path variables (``<path:...>``) we use ``.+`` to match any
        # characters including slashes. For all other variable types we use
        # ``[^/]+`` to match a single path segment. We deliberately do not use
        # each converter's own (stricter) regex: requests with the "wrong" type
        # should still be forwarded to the Flask app so that it can produce the
        # appropriate response (e.g. a 404). Literal parts are kept literal.
        path_to_match = _rule_to_path_regex(rule=rule)
        escaped_base_url = re.escape(pattern=base_url)
        patterns = [urljoin(base=escaped_base_url, url=path_to_match)]
        has_slashless_redirect = (
            rule.strict_slashes
            and path_to_match.endswith("/")
            and path_to_match != "/"
        )
        if path_to_match == "/":
            patterns.append(patterns[0].rstrip("/"))
        elif has_slashless_redirect:
            patterns.append(
                urljoin(base=escaped_base_url, url=path_to_match.rstrip("/"))
            )
        urls = tuple(
            re.compile(pattern=pattern + r"(\?.*)?$") for pattern in patterns
        )

        methods = (rule.methods or set()) | _KNOWN_HTTP_METHODS
        for method in methods:
            for url in urls:
                _register_mock(
                    mock_obj=mock_obj,
                    method=method,
                    url=url,
                    callbacks=callbacks,
                )


def _rule_to_path_regex(rule: Rule) -> str:
    """Return a regex that matches the path part of a Flask routing
    rule.
    """
    rule.compile()
    path_parts: list[str] = []
    rule_attributes: Any = vars(rule)
    rule_trace = rule_attributes["_trace"]
    rule_converters = rule_attributes["_converters"]
    separator_index = rule_trace.index((False, "|"))
    for is_dynamic, data in rule_trace[separator_index + 1 :]:
        if is_dynamic:
            converter = rule_converters[data]
            path_parts.append(converter.regex)
        else:
            encoded_literal = quote(string=data, safe="/")
            path_parts.append(re.escape(pattern=encoded_literal))
    return "".join(path_parts)


def _responses_callback(
    request: requests.PreparedRequest,
    flask_app: flask.Flask,
) -> tuple[int, HTTPHeaderDict, bytes]:
    """Given a request to the flask app, send an equivalent request to an
    in
    memory fake of the flask app and return some key details of the
    response.

    :param request: The incoming request to pass onto the flask app.
    :param flask_app: The Flask application to pass requests to.
    :return: A tuple of status code, response headers and response data
        from the flask app.
    """
    # We disable the test client's cookie jar so that the original ``Cookie``
    # header is forwarded to the Flask app untouched. This preserves duplicate
    # cookies with the same name and other multi-value header semantics.
    test_client = flask_app.test_client(use_cookies=False)
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]

    headers_dict = _without_transfer_encoding(
        headers=dict(request.headers).items(),
    )
    split_url = urlsplit(url=str(object=request.url))
    base_url = f"{split_url.scheme}://{split_url.netloc}/"
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path_url,
        base_url=base_url,
        method=str(object=request.method),
        data=_normalize_body(body=request.body),
        headers=headers_dict,
        environ_overrides=environ_overrides,
    )

    with test_client.open(environ_builder.get_request()) as response:
        return (
            response.status_code,
            HTTPHeaderDict(headers=response.headers),
            bytes(response.data),
        )


def _httpretty_callback(
    request: httpretty.core.HTTPrettyRequest,
    uri: str,
    headers: dict[str, Any],
    flask_app: flask.Flask,
) -> tuple[int, HTTPHeaderDict, bytes]:
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
    del headers

    # We disable the test client's cookie jar so that the original ``Cookie``
    # header is forwarded to the Flask app untouched. This preserves duplicate
    # cookies with the same name and other multi-value header semantics.
    test_client = flask_app.test_client(use_cookies=False)
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]

    split_url = urlsplit(url=uri)
    base_url = f"{split_url.scheme}://{split_url.netloc}/"
    environ_builder = werkzeug.test.EnvironBuilder(
        path=str(object=request.path),
        base_url=base_url,
        method=request.method,
        headers=request.headers.items(),
        data=request.body,
        environ_overrides=environ_overrides,
    )
    with test_client.open(environ_builder.get_request()) as response:
        http_module: Any = vars(httpretty)["http"]
        statuses: dict[int, str] = http_module.STATUSES
        if response.status_code not in statuses:
            _, _, reason_phrase = response.status.partition(" ")
            statuses[response.status_code] = reason_phrase

        return (
            response.status_code,
            HTTPHeaderDict(headers=response.headers),
            response.data,
        )


def _requests_mock_callback(
    request: requests_mock.Request,
    context: requests_mock.Context,
    flask_app: flask.Flask,
) -> bytes:
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
    # We disable the test client's cookie jar so that the original ``Cookie``
    # header is forwarded to the Flask app untouched. This preserves duplicate
    # cookies with the same name and other multi-value header semantics.
    test_client = flask_app.test_client(use_cookies=False)
    # See parameters at
    # https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.EnvironBuilder
    environ_overrides: dict[str, str] = {}
    if "Content-Length" in request.headers:
        environ_overrides["CONTENT_LENGTH"] = request.headers["Content-Length"]
    split_url = urlsplit(url=str(object=request.url))
    base_url = f"{split_url.scheme}://{split_url.netloc}/"
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path_url,
        base_url=base_url,
        method=request.method,
        headers=_without_transfer_encoding(headers=request.headers.items()),
        data=_normalize_body(body=request.body),
        environ_overrides=environ_overrides,
    )
    with test_client.open(environ_builder.get_request()) as response:
        # requests-mock exposes headers as ``dict[str, str]``, so its callback
        # context cannot represent repeated fields.
        # ``response.status`` is the full WSGI status line, so preserve its
        # reason phrase through the requests-mock callback context.
        _, _, reason_phrase = response.status.partition(" ")
        context.headers = dict(response.headers)
        context.status_code = response.status_code
        context.reason = reason_phrase
        return bytes(response.data)
