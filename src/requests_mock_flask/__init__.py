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
        # We assume here that everything is in the style:
        # "{uri}/{method}/<{id}>" or "{uri}/{method}" or
        # "{uri}/{method}/<{type}:{id}>" when this is not necessarily the case.
        #
        # We replace everything inside angle brackets with a match for any
        # string of characters of length > 0.
        path_to_match = re.sub(pattern='<.+>', repl='.+', string=rule.rule)
        pattern = urljoin(base_url, path_to_match)

        for method in rule.methods:
            mock_obj.add_callback(
                # ``responses`` has methods named like the HTTP methods
                # they represent, e.g. ``responses.GET``.
                method=getattr(responses, method),
                url=re.compile(pattern),
                callback=callback,
            )


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
    # The Flask test client is a ``werkzeug.test.Client`` and therefore has
    # methods like 'head', 'get' and 'post'.
    lower_request_method = str(request.method).lower()
    test_client = flask_app.test_client()
    test_client_method = getattr(test_client, lower_request_method)
    response = test_client_method(
        path=request.path_url,
        headers=dict(request.headers),
        data=request.body,
    )

    result = (response.status_code, dict(response.headers), response.data)
    return result
