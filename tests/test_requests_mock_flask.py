"""
Tests for the ``requests_mock_flask`` package.
"""

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
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert response.data == b'Hello, World!'

def test_route_with_json():
    app = Flask(__name__)

    @app.route('/')
    def example() -> Tuple[Response, int]:
        return jsonify({'hello': 'world'})

    test_client = app.test_client()
    response = test_client.get('/')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    expected_data = {'hello': 'world'}
    assert response.json == expected_data

def test_route_with_variable_no_type_given():

    app = Flask(__name__)

    @app.route('/<my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable


def test_route_with_string_variable():

    app = Flask(__name__)

    @app.route('/<string:my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable


def test_route_with_int_variable():
    app = Flask(__name__)

    @app.route('/<int:my_variable>')
    def example(my_variable: int) -> Tuple[Response, int]:
        return 'Hello: ' + str(my_variable + 5)

def test_route_with_float_variable():
    app = Flask(__name__)

    @app.route('/<int:my_variable>')
    def example(my_variable: float) -> Tuple[Response, int]:
        return 'Hello: ' + str(my_variable + 5)

def test_route_with_path_variable_with_slash():
    app = Flask(__name__)

    @app.route('/<path:my_variable>')
    def example(my_variable: str) -> Tuple[Response, int]:
        return 'Hello: ' + my_variable

def test_route_with_uuid_variable():
    # TODO
    pass

def test_nested_path():
    # TODO variable after a non-variable, and then with another path after?
    pass

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


# TODO link to https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
# TODO test with a custom converter

# TODO with requests_mock
# TODO with responses
# TODO maybe a for loop for each converter in url_map.converters
