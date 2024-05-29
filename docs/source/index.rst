|project|
=========

|project| helps with testing `Flask`_ applications with `responses`_ or `requests-mock`_.

Installation
------------

Requires Python 3.12+.

.. code:: sh

   pip install requests-mock-flask


Usage example
-------------

.. code:: python

   import flask
   import httpretty
   import requests
   import responses
   import requests_mock

   from requests_mock_flask import add_flask_app_to_mock

   app = flask.Flask("test_app")

   @app.route('/')
   def _() -> str:
        return 'Hello, World!'

   @responses.activate
   def test_responses_decorator() -> None:
       """
       It is possible to use the helper with a ``responses`` decorator.
       """
       add_flask_app_to_mock(
           mock_obj=responses,
           flask_app=app,
           base_url='http://www.example.com',
       )

       response = requests.get('http://www.example.com')

       assert response.status_code == 200
       assert response.text == 'Hello, World!'

   def test_responses_context_manager() -> None:
       """
       It is possible to use the helper with a ``responses`` context manager.
       """
       with responses.RequestsMock(
           assert_all_requests_are_fired=False,
       ) as resp_m:
           add_flask_app_to_mock(
               mock_obj=resp_m,
               flask_app=app,
               base_url='http://www.example.com',
           )

           response = requests.get('http://www.example.com')

       assert response.status_code == 200
       assert response.text == 'Hello, World!'

   def test_requests_mock_context_manager() -> None:
       """
       It is possible to use the helper with a ``requests_mock`` context
       manager.
       """
       with requests_mock.Mocker() as resp_m:
           add_flask_app_to_mock(
               mock_obj=resp_m,
               flask_app=app,
               base_url='http://www.example.com',
           )

           response = requests.get('http://www.example.com')

       assert response.status_code == 200
       assert response.text == 'Hello, World!'

   def test_requests_mock_adapter() -> None:
       """
       It is possible to use the helper with a ``requests_mock`` fixture.
       """
       session = requests.Session()
       adapter = requests_mock.Adapter()
       session.mount('mock', adapter)

       add_flask_app_to_mock(
           mock_obj=adapter,
           flask_app=app,
           base_url='mock://www.example.com',
       )

       response = session.get('mock://www.example.com')

       assert response.status_code == 200
       assert response.text == 'Hello, World!'

   def test_httpretty_context_manager() -> None:
       """
       It is possible to use the helper with a ``httpretty`` context
       manager.
       """
       with httpretty.core.httprettized():
           add_flask_app_to_mock(
               mock_obj=httpretty,
               flask_app=app,
               base_url='http://www.example.com',
           )

           response = requests.get('http://www.example.com')

       assert response.status_code == 200
       assert response.text == 'Hello, World!'

.. -> test_src

.. invisible-code-block: python

   import pathlib
   import subprocess
   import tempfile

   import pytest

   with tempfile.TemporaryDirectory() as tmp_dir:
       test_file = pathlib.Path(tmp_dir) / 'test_src.py'
       test_file.write_text(test_src)
       subprocess.check_output(["python", "-m", "pytest", test_file, "--basetemp", test_file.parent])

Use cases
---------

* Use the ``requests`` for testing applications.
* Create a test suite which can test a Flask application as well as a live web application, to make a verified fake.
* Test a service which calls a Flask application that you have the source code for.

Reference
---------

.. toctree::
   :maxdepth: 3

   api-reference
   release-process
   changelog
   contributing

.. _Flask: https://flask.palletsprojects.com/
.. _requests-mock: https://requests-mock.readthedocs.io/en/latest/
.. _responses: https://github.com/getsentry/responses
