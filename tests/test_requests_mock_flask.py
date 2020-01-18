"""
Tests for the ``requests_mock_flask`` package.

Test with a bunch of route types as per:
https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
"""

import uuid
from typing import Tuple
from flask_negotiate import consumes


from flask import Flask, Response, jsonify


def test_simple_route() -> None:
    """
    A simple GET route works.
    """
    app = Flask(__name__)

    @app.route('/')
    def _() -> str:
        return 'Hello, World!'

    test_client = app.test_client()
    response = test_client.get('/')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_json() -> None:
    """
    A route that returns JSON data works.
    """
    app = Flask(__name__)

    @app.route('/')
    def _() -> Tuple[Response, int]:
        return jsonify({'hello': 'world'}), 201

    test_client = app.test_client()
    response = test_client.get('/')

    expected_status_code = 201
    expected_content_type = 'application/json'
    expected_json = {'hello': 'world'}

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.json == expected_json


def test_route_with_variable_no_type_given() -> None:
    """
    A route with a variable works.
    """
    app = Flask(__name__)

    @app.route('/<my_variable>')
    def _(my_variable: str) -> str:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/Frasier')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: Frasier'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_string_variable() -> None:
    """
    A route with a string variable works.
    """
    app = Flask(__name__)

    @app.route('/<string:my_variable>')
    def _(my_variable: str) -> str:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/Frasier')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: Frasier'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_int_variable() -> None:
    """
    A route with an int variable works.
    """
    app = Flask(__name__)

    @app.route('/<int:my_variable>')
    def _(my_variable: int) -> str:
        return 'Hello: ' + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get('/4')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: 9'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_float_variable() -> None:
    """
    A route with a float variable works.
    """
    app = Flask(__name__)

    @app.route('/<float:my_variable>')
    def _(my_variable: float) -> str:
        return 'Hello: ' + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get('/4.0')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: 9.0'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_path_variable_with_slash() -> None:
    """
    A route with a path variable works.
    """
    app = Flask(__name__)

    @app.route('/<path:my_variable>')
    def _(my_variable: str) -> str:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/foo/bar')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: foo/bar'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_uuid_variable() -> None:
    """
    A route with a uuid variable works.
    """
    app = Flask(__name__)

    @app.route('/<uuid:my_variable>')
    def _(my_variable: uuid.UUID) -> str:
        return 'Hello: ' + my_variable.hex

    test_client = app.test_client()
    random_uuid = uuid.uuid4()
    response = test_client.get(f'/{random_uuid}')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = bytes(f'Hello: {random_uuid.hex}', 'utf-8')

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_nested_path() -> None:
    """
    A route with a variable nested in a path works.
    """
    app = Flask(__name__)

    @app.route('/users/<int:my_variable>/posts')
    def _(my_variable: int) -> str:
        return 'Posts for: ' + str(my_variable)

    test_client = app.test_client()
    response = test_client.get('/users/4/posts')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Posts for: 4'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_multiple_variables() -> None:
    """
    A route with multiple variables works.
    """
    app = Flask(__name__)

    @app.route('/users/<string:my_org>/<string:my_user>/posts')
    def _(my_org: str, my_user: str) -> str:
        return 'Posts for: ' + my_org + '/' + my_user

    test_client = app.test_client()
    response = test_client.get('/users/cranes/frasier/posts')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Posts for: cranes/frasier'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_post_verb() -> None:
    """
    A route with the POST verb works.
    """
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def _() -> str:
        return 'Hello, World!'

    test_client = app.test_client()
    response = test_client.post('/')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_multiple_http_verbs() -> None:
    """
    A route with multiple verbs works.
    """
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def _() -> str:
        return 'Hello, World!'

    test_client = app.test_client()
    get_response = test_client.get('/')
    post_response = test_client.post('/')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert get_response.status_code == expected_status_code
    assert get_response.headers['Content-Type'] == expected_content_type
    assert get_response.data == expected_data

    assert post_response.status_code == expected_status_code
    assert post_response.headers['Content-Type'] == expected_content_type
    assert post_response.data == expected_data


def test_wrong_type_given() -> None:
    """
    A route with the wrong type given works.
    """
    app = Flask(__name__)

    @app.route('/<int:my_variable>')
    def _(_: int) -> str:
        ...  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get('/a')

    expected_status_code = 404
    expected_content_type = 'text/html'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert b'not found on the server' in response.data


def test_404_no_such_method() -> None:
    """
    A route with the wrong method given works.
    """
    app = Flask(__name__)

    @app.route('/')
    def _() -> str:
        ...  # pragma: no cover

    test_client = app.test_client()
    response = test_client.post('/')

    expected_status_code = 405
    expected_content_type = 'text/html'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert b'not allowed for the requested URL.' in response.data


def test_request_needs_content_type() -> None:
    """
    Routes which require a content type are supported.
    """
    app = Flask(__name__)

    @app.route('/')
    @consumes('application/json')
    def _() -> str:
        return 'Hello, World!'

    test_client = app.test_client()
    response = test_client.get('/', content_type='application/json')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data
