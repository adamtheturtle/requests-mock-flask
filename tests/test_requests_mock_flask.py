"""
Tests for the ``requests_mock_flask`` package.
"""

from flask import Flask

def test_flask_client() -> None:
    """
    Test with a trivial Flask application.
    """
    trivial_flask_app = Flask(__name__)

    @trivial_flask_app.route('/')
    def hello_world():
        return 'Hello, World!'

    test_client = trivial_flask_app.test_client()
    result = test_client.get('/')
    assert result.status_code == 200
    assert result.headers['Content-Type'] == 'text/html; charset=utf-8'
