"""
Package for ``requests_mock_flask``.
"""

import re
from functools import partial
from typing import Dict, Optional, Tuple, Union
from urllib.parse import urljoin

import responses
from flask import Flask
from requests import PreparedRequest
from werkzeug.http import parse_cookie



def add_flask_app_to_mock(
    mock_obj: responses.RequestsMock,
    flask_app: Flask,
    base_url: str,
) -> None:
    """
    Make it so that requests sent to the ``base_url`` are forwarded to the
    ``Flask`` app, when in the context of the ``mock_obj``.
    """
    callback = partial(_request_callback, flask_app=flask_app)
    for rule in flask_app.url_map.iter_rules():
        # We replace everything inside angle brackets with a match for any
        # string of characters of length > 0.
        path_to_match = re.sub(pattern='<.+>', repl='.+', string=rule.rule)
        pattern = urljoin(base_url, path_to_match)
        url = re.compile(pattern)

        for method in rule.methods:
            mock_obj.add_callback(method=method, url=url, callback=callback)


def _request_callback(
    request: PreparedRequest,
    flask_app: Flask,
) -> Tuple[int, Dict[str, Optional[Union[str, int, bool]]], bytes]:
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
    # import pdb; pdb.set_trace()
    request_cookies = [list(parse_cookie(cookie).items())[0] for cookie in cookie_list_no_empty]
    cookies_dict = dict(request_cookies)

    for key, value in cookies_dict.items():
        test_client.set_cookie(
            server_name='',
            key=key,
            value=value,
        )

    response = test_client.open(
        path=request.path_url,
        method=request.method,
        headers=dict(request.headers),
        data=request.body,
    )

    result = (response.status_code, dict(response.headers), response.data)
    return result
