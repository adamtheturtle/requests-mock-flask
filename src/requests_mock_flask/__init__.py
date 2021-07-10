"""
Package for ``requests_mock_flask``.
"""

from __future__ import annotations

import re
from functools import partial
from typing import Any, Dict, Tuple, Union
from urllib.parse import urljoin

import werkzeug
from flask import Flask
from requests import PreparedRequest
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context
from werkzeug.http import parse_cookie


def add_flask_app_to_mock(
    # We use the ``Any`` type to support:
    # ``requests_mock.Mocker, ``responses.RequestsMock`` and the ``responses``
    # module.
    mock_obj: Any,
    flask_app: Flask,
    base_url: str,
) -> None:
    """
    Make it so that requests sent to the ``base_url`` are forwarded to the
    ``Flask`` app, when in the context of the ``mock_obj``.
    """
    if hasattr(mock_obj, 'add_callback'):
        resp_callback = partial(_responses_callback, flask_app=flask_app)
        register_method = partial(
            mock_obj.add_callback,
            callback=resp_callback,
        )
    else:
        req_m_callback = partial(_requests_mock_callback, flask_app=flask_app)
        register_method = partial(mock_obj.register_uri, text=req_m_callback)

    for rule in flask_app.url_map.iter_rules():
        # We replace everything inside angle brackets with a match for any
        # string of characters of length > 0.
        path_to_match = re.sub(pattern='<.+>', repl='.+', string=rule.rule)
        pattern = urljoin(base_url, path_to_match)
        url = re.compile(pattern)

        assert rule.methods is not None
        for method in rule.methods:
            register_method(method=method, url=url)


def _responses_callback(
    request: PreparedRequest,
    flask_app: Flask,
) -> Tuple[int, Dict[str, str | int | bool | None], bytes]:
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
    cookie_string = request.headers.get('Cookie', '')
    cookie_list = cookie_string.split(';')
    cookie_list_no_empty = [item for item in cookie_list if item]
    request_cookies = [
        list(parse_cookie(cookie).items())[0]
        for cookie in cookie_list_no_empty
    ]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name='',
            key=key,
            value=value,
        )

    environ_overrides = {}
    if 'Content-Length' in request.headers:
        environ_overrides['CONTENT_LENGTH'] = request.headers['Content-Length']

    headers_dict = dict(request.headers).items()
    environ_builder = werkzeug.test.EnvironBuilder(
        path=request.path_url,
        method=str(request.method),
        data=request.body,
        headers=headers_dict,
        environ_overrides=environ_overrides,
    )

    response = test_client.open(environ_builder.get_request())

    result_headers: Dict[str, Union[str, int, bool, None]] = dict(
        response.headers,
    )
    result = (response.status_code, result_headers, bytes(response.data))
    return result


def _requests_mock_callback(
    request: _RequestObjectProxy,
    context: _Context,
    flask_app: Flask,
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
    cookie_string = request.headers.get('Cookie', '')
    cookie_list = cookie_string.split(';')
    cookie_list_no_empty = [item for item in cookie_list if item]
    request_cookies = [
        list(parse_cookie(cookie).items())[0]
        for cookie in cookie_list_no_empty
    ]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name='',
            key=key,
            value=value,
        )

    environ_overrides = {}
    if 'Content-Length' in request.headers:
        environ_overrides['CONTENT_LENGTH'] = request.headers['Content-Length']
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
