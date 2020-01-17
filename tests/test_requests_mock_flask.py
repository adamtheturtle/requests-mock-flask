"""
Tests for the ``requests_mock_flask`` package.
"""

from typing import Tuple

from flask import Flask, Response, jsonify

def test_simple_route() -> None:
    """
    Test with a trivial Flask application.
    """
    trivial_flask_app = Flask(__name__)

    @trivial_flask_app.route('/')
    def example() -> str:
        return 'Hello, World!'

    test_client = trivial_flask_app.test_client()
    result = test_client.get('/')
    assert result.status_code == 200
    assert result.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert response.text == 'Hello World!'

def test_route_with_json():
    trivial_flask_app = Flask(__name__)

    @trivial_flask_app.route('/something_json')
    def example() -> Tuple[Response, int]:
        return jsonify({'hello': 'world'})

    @trivial_flask_app.route('/something_json/<int: example_id>')
    def example(example_id: int) -> Tuple[Response, int]:
        return jsonify({'hello': 'world'})

    test_client = trivial_flask_app.test_client()
    result = test_client.get('/')
    assert result.status_code == 200
    assert result.headers['Content-Type'] == 'application/json'
    assert response.text == 'Hello World!'

def test_route_with_string_variable():
    pass

def test_route_with_int_variable():
    pass

def test_route_with_float_variable():
    pass

def test_route_with_path_variable():
    pass

def test_route_with_uuid_variable():
    pass

def test_route_with_multiple_variables():
    pass

def test_post_verb():
    pass

def test_multiple_http_verbs():
    pass

def test_custom_converter():
    pass


# TODO link to https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
# TODO test with a custom converter

# TODO with requests_mock
# TODO with responses
# TODO maybe a for loop for each converter in url_map.converters
