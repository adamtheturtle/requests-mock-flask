"""
Tests for the ``requests_mock_flask`` package.
"""

import uuid
from typing import Tuple

from flask import Flask, Response, jsonify

def test_simple_route() -> None:
    """
    Test with a trivial Flask application.
    """
    app = Flask(__name__)

    @app.route('/')
    def example() -> str:
        return 'Hello, World!'

    test_client = app.test_client()
    response = test_client.get('/')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

def test_route_with_json():
    app = Flask(__name__)

    @app.route('/')
    def example() -> Tuple[Response, int]:
        return jsonify({'hello': 'world'})

    test_client = app.test_client()
    response = test_client.get('/')

    expected_status_code = 200
    expected_content_type = 'application/json'
    expected_json = {'hello': 'world'}

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.json == expected_json

def test_route_with_variable_no_type_given():

    app = Flask(__name__)

    @app.route('/<my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/Frasier')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: Frasier'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_string_variable():

    app = Flask(__name__)

    @app.route('/<string:my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/Frasier')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: Frasier'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_int_variable():
    app = Flask(__name__)

    @app.route('/<int:my_variable>')
    def example(my_variable: int) -> Tuple[Response, int]:
        return 'Hello: ' + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get('/4')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: 9'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

def test_route_with_float_variable():
    app = Flask(__name__)

    @app.route('/<float:my_variable>')
    def example(my_variable: float) -> Tuple[Response, int]:
        return 'Hello: ' + str(my_variable + 5)

    test_client = app.test_client()
    response = test_client.get('/4.0')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: 9.0'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data


def test_route_with_path_variable_with_slash():
    app = Flask(__name__)

    @app.route('/<path:my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable

    test_client = app.test_client()
    response = test_client.get('/foo/bar')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: foo/bar'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

def test_route_with_uuid_variable():
    app = Flask(__name__)

    @app.route('/<uuid:my_variable>')
    def example(my_variable: uuid.UUID) -> Tuple[Response, int]:
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

def test_nested_path():
    app = Flask(__name__)

    @app.route('/users/<int:my_variable>/posts')
    def example(my_variable: int) -> Tuple[Response, int]:
        return 'Posts for: ' + str(my_variable)

    test_client = app.test_client()
    response = test_client.get('/users/4/posts')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Posts for: 4'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

def test_route_with_multiple_variables():
    pass

def test_post_verb():
    pass

def test_multiple_http_verbs():
    pass

def test_wrong_type_given():
    pass

def test_custom_converter():
    pass

def test_404_no_such_path():
    pass

def test_404_no_such_method():
    pass


# TODO link to https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
# TODO test with a custom converter
#  - (maybe https://github.com/wbolster/flask-uuid with strict=False?)

# TODO with requests_mock
# TODO with responses
# TODO maybe a for loop for each converter in url_map.converters
