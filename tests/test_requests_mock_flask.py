# pylint: disable=too-many-lines
"""
Tests for the ``requests_mock_flask`` package.

Test with a bunch of route types as per:
https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
"""

import json
import uuid
from typing import Tuple

import pytest
import requests
import requests_mock
import responses
import werkzeug
from flask import Flask, Response, jsonify, make_response, request
from flask_negotiate import consumes

from requests_mock_flask import add_flask_app_to_mock


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_headers() -> None:
    """
    Request headers are sent.
    """
    app = Flask(__name__)

    @app.route('/')
    def _() -> str:
        assert 'Content-Type' not in request.headers
        assert request.headers['hello'] == 'world'
        return 'Hello, World!'

    test_client = app.test_client()
    response = test_client.get('/', headers={'hello': 'world'})

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com',
            headers={'hello': 'world'},
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com',
            headers={'hello': 'world'},
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.json() == expected_json

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.json() == expected_json


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/Frasier')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/Frasier')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/Frasier')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/Frasier')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/4')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/4')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/4.0')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/4.0')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/foo/bar')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/foo/bar')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_route_with_string_variable_with_slash() -> None:
    """
    A route with a string variable when given a slash works.
    """
    app = Flask(__name__)

    @app.route('/<string:my_variable>')
    def _(_: str) -> str:
        ...  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get('/foo/bar')

    expected_status_code = 404
    expected_content_type = 'text/html; charset=utf-8'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert b'not found on the server' in response.data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/foo/bar')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert 'not found on the server' in responses_response.text

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/foo/bar')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert 'not found on the server' in req_mock_response.text


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            f'http://www.example.com/{random_uuid}',
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            f'http://www.example.com/{random_uuid}',
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com/users/4/posts',
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com/users/4/posts',
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com/users/cranes/frasier/posts',
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com/users/cranes/frasier/posts',
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.post('http://www.example.com/')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.post('http://www.example.com/')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


@pytest.mark.parametrize(
    'custom_content_length',
    ['1', '100'],
)
def test_incorrect_content_length(custom_content_length: str) -> None:
    """
    Custom content length headers are passed through to the Flask endpoint.
    """
    app = Flask(__name__)
    data = b'12345'

    @app.route('/', methods=['POST'])
    def _() -> str:
        request.environ['wsgi.input_terminated'] = True
        assert len(data) == len(request.data)
        assert request.headers['Content-Length'] == custom_content_length
        return ''

    test_client = app.test_client()
    environ_builder = werkzeug.test.EnvironBuilder(
        path='/',
        method='POST',
        data=b'12345',
        environ_overrides={'CONTENT_LENGTH': custom_content_length},
    )

    response = test_client.open(environ_builder.get_request())

    expected_status_code = 200

    assert response.status_code == expected_status_code

    requests_request = requests.Request(
        method='POST',
        url='http://www.example.com/',
        data=data,
    ).prepare()
    requests_request.headers['Content-Length'] = custom_content_length

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        session = requests.Session()
        responses_response = session.send(request=requests_request)

    assert responses_response.status_code == expected_status_code

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        session = requests.Session()
        req_mock_response = session.send(request=requests_request)

    assert req_mock_response.status_code == expected_status_code


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_get_response = requests.get('http://www.example.com/')
        responses_post_response = requests.post('http://www.example.com/')

    assert responses_get_response.status_code == expected_status_code
    assert (
        responses_get_response.headers['Content-Type'] == expected_content_type
    )
    assert responses_get_response.text == expected_data.decode()

    assert responses_post_response.status_code == expected_status_code
    assert (
        responses_post_response.headers['Content-Type']
        == expected_content_type
    )
    assert responses_post_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_get_response = requests.get('http://www.example.com/')
        req_mock_post_response = requests.post('http://www.example.com/')

    assert req_mock_get_response.status_code == expected_status_code
    assert (
        req_mock_get_response.headers['Content-Type'] == expected_content_type
    )
    assert req_mock_get_response.text == expected_data.decode()

    assert req_mock_post_response.status_code == expected_status_code
    assert (
        req_mock_post_response.headers['Content-Type'] == expected_content_type
    )
    assert req_mock_post_response.text == expected_data.decode()


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
    expected_content_type = 'text/html; charset=utf-8'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert b'not found on the server' in response.data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/a')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert 'not found on the server' in responses_response.text

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/a')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert 'not found on the server' in req_mock_response.text


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
    expected_content_type = 'text/html; charset=utf-8'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert b'not allowed for the requested URL.' in response.data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        with pytest.raises(requests.exceptions.ConnectionError):
            requests.post('http://www.example.com/')

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        with pytest.raises(requests_mock.exceptions.NoMockAddress):
            requests.post('http://www.example.com/')


def test_request_needs_content_type() -> None:
    """
    Routes which require a content type are supported.
    """
    app = Flask(__name__)

    @app.route('/')
    @consumes('application/json')  # type: ignore
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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com',
            headers={'Content-Type': 'application/json'},
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com',
            headers={'Content-Type': 'application/json'},
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_request_needs_data() -> None:
    """
    Routes which require data are supported.
    """
    app = Flask(__name__)

    @app.route('/')
    @consumes('application/json')  # type: ignore
    def _() -> str:
        request_json = request.get_json()
        assert isinstance(request_json, dict)
        return str(request_json['hello'])

    test_client = app.test_client()
    response = test_client.get(
        '/',
        content_type='application/json',
        data=json.dumps({'hello': 'world'}),
    )

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'world'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'hello': 'world'}),
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'hello': 'world'}),
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_multiple_functions_same_path_different_type() -> None:
    """
    When multiple functions exist with the same path but have a different type,
    the mock matches them just the same.
    """
    app = Flask(__name__)

    @app.route('/<my_variable>')
    def _(_: float) -> str:
        ...  # pragma: no cover

    @app.route('/<int:my_variable>')
    def ___(my_variable: int) -> str:
        return 'Is int: ' + str(my_variable)

    @app.route('/<string:my_variable>')
    def ____(_: str) -> str:
        ...  # pragma: no cover

    test_client = app.test_client()
    response = test_client.get('/4')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Is int: 4'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get('http://www.example.com/4')

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get('http://www.example.com/4')

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_query_string() -> None:
    """
    Query strings work.
    """
    app = Flask(__name__)

    @app.route('/')
    def _() -> str:
        result = request.args['frasier']
        return 'Hello: ' + str(result)

    test_client = app.test_client()
    response = test_client.get('/?frasier=crane')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello: crane'

    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.get(
            'http://www.example.com?frasier=crane',
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.get(
            'http://www.example.com?frasier=crane',
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()


def test_cookies() -> None:
    """
    Cookies work.
    """
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def _() -> Response:
        response = make_response()
        response.set_cookie('frasier_set', 'crane_set')
        assert request.cookies['frasier'] == 'crane'
        assert request.cookies['frasier2'] == 'crane2'
        response.data = 'Hello, World!'
        assert isinstance(response, Response)
        return response

    test_client = app.test_client()
    test_client.set_cookie(server_name='', key='frasier', value='crane')
    test_client.set_cookie(server_name='', key='frasier2', value='crane2')
    test_client_cookie_jar = test_client.cookie_jar
    assert test_client_cookie_jar is not None
    original_cookies = set(test_client_cookie_jar)
    response = test_client.post('/')

    expected_status_code = 200
    expected_content_type = 'text/html; charset=utf-8'
    expected_data = b'Hello, World!'

    (new_cookie,) = set(test_client_cookie_jar) - original_cookies
    assert new_cookie.name == 'frasier_set'
    assert new_cookie.value == 'crane_set'
    assert response.status_code == expected_status_code
    assert response.headers['Content-Type'] == expected_content_type
    assert response.data == expected_data

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        responses_response = requests.post(
            'http://www.example.com',
            cookies={
                'frasier': 'crane',
                'frasier2': 'crane2',
            },
        )

    assert responses_response.status_code == expected_status_code
    assert responses_response.headers['Content-Type'] == expected_content_type
    assert responses_response.text == expected_data.decode()
    assert responses_response.cookies['frasier_set'] == 'crane_set'

    with requests_mock.Mocker() as resp_m:
        add_flask_app_to_mock(
            mock_obj=resp_m,
            flask_app=app,
            base_url='http://www.example.com',
        )

        req_mock_response = requests.post(
            'http://www.example.com',
            cookies={
                'frasier': 'crane',
                'frasier2': 'crane2',
            },
        )

    assert req_mock_response.status_code == expected_status_code
    assert req_mock_response.headers['Content-Type'] == expected_content_type
    assert req_mock_response.text == expected_data.decode()
    assert req_mock_response.cookies['frasier_set'] == 'crane_set'
