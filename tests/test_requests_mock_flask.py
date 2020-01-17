"""
Tests for the ``requests_mock_flask`` package.
"""

from flask import Flask, jsonify

def test_flask_client() -> None:
    """
    Test with a trivial Flask application.
    """
    trivial_flask_app = Flask(__name__)

    @trivial_flask_app.route('/')
    def hello_world():
        return 'Hello, World!'

    @trivial_flask_app.route('/something_json')
    def hello_world_json():
        return jsonify({'hello': 'world'})

    @trivial_flask_app.route('/something_json/<')
    def hello_world_with_id():
        return jsonify({'hello': 'world'})

    # TODO something with each ID pattern
    # TODO something with a different HTTP verb

    test_client = trivial_flask_app.test_client()
    result = test_client.get('/')
    assert result.status_code == 200
    assert result.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert response.text == 'Hello World!'

    # TODO with requests_mock
    # TODO with responses
