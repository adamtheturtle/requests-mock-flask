"""
Tests for the ``requests_mock_flask`` package.
"""

from tests.trivial_flask_app import TRIVIAL_FLASK_APP


def test_flask_client() -> None:
    """
    """
    test_client = TRIVIAL_FLASK_APP.test_client()
