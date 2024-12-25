|Build Status| |codecov| |PyPI| |Documentation Status|

requests-mock-flask
===================

``requests-mock-flask`` helps with testing `Flask`_ applications with `httpretty`_, `responses`_ or `requests-mock`_.

.. contents::
   :local:

Installation
------------

Requires Python |minimum-python-version|\+.

.. code-block:: sh

   pip install requests-mock-flask


Usage example
-------------

.. code-block:: python

   """
   Examples of using requests-mock-flask with responses, requests-mock
   and httpretty.
   """

   from http import HTTPStatus

   import flask
   import httpretty  # type: ignore[import-untyped]
   import requests
   import requests_mock
   import responses

   from requests_mock_flask import add_flask_app_to_mock

   app = flask.Flask(import_name="test_app")


   @app.route(rule="/")
   def _() -> str:
       """Return a simple message."""
       return "Hello, World!"


   @responses.activate
   def test_responses_decorator() -> None:
       """
       It is possible to use the helper with a ``responses`` decorator.
       """
       add_flask_app_to_mock(
           mock_obj=responses,
           flask_app=app,
           base_url="http://www.example.com",
       )

       response = requests.get(url="http://www.example.com", timeout=30)

       assert response.status_code == HTTPStatus.OK
       assert response.text == "Hello, World!"


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
               base_url="http://www.example.com",
           )

           response = requests.get(url="http://www.example.com", timeout=30)

           assert response.status_code == HTTPStatus.OK
           assert response.text == "Hello, World!"


   def test_requests_mock_context_manager() -> None:
       """
       It is possible to use the helper with a ``requests_mock`` context
       manager.
       """
       with requests_mock.Mocker() as resp_m:
           add_flask_app_to_mock(
               mock_obj=resp_m,
               flask_app=app,
               base_url="http://www.example.com",
           )

           response = requests.get(url="http://www.example.com", timeout=30)

       assert response.status_code == HTTPStatus.OK
       assert response.text == "Hello, World!"


   def test_requests_mock_adapter() -> None:
       """
       It is possible to use the helper with a ``requests_mock`` fixture.
       """
       session = requests.Session()
       adapter = requests_mock.Adapter()
       session.mount(prefix="mock", adapter=adapter)

       add_flask_app_to_mock(
           mock_obj=adapter,
           flask_app=app,
           base_url="mock://www.example.com",
       )

       response = session.get(url="mock://www.example.com", timeout=30)

       assert response.status_code == HTTPStatus.OK
       assert response.text == "Hello, World!"


   def test_httpretty_context_manager() -> None:
       """
       It is possible to use the helper with a ``httpretty`` context
       manager.
       """
       with httpretty.core.httprettized():
           add_flask_app_to_mock(
               mock_obj=httpretty,
               flask_app=app,
               base_url="http://www.example.com",
           )

           response = requests.get(url="http://www.example.com", timeout=30)

       assert response.status_code == HTTPStatus.OK
       assert response.text == "Hello, World!"

Use cases
---------

* Use ``requests`` or other Python APIs for testing Flask applications.
* Create a test suite which can test a Flask application as well as a live web application, to make a verified fake.
* Test a service which calls a Flask application that you have the source code for.


Full documentation
------------------

See the `full documentation <https://requests-mock-flask.readthedocs.io/en/latest>`__ for more information including how to contribute.

.. _Flask: https://flask.palletsprojects.com/
.. _requests-mock: https://requests-mock.readthedocs.io/en/latest/
.. _responses: https://github.com/getsentry/responses
.. _httpretty: https://httpretty.readthedocs.io

.. |Build Status| image:: https://github.com/adamtheturtle/requests-mock-flask/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/adamtheturtle/requests-mock-flask/actions
.. |codecov| image:: https://codecov.io/gh/adamtheturtle/requests-mock-flask/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/adamtheturtle/requests-mock-flask
.. |Documentation Status| image:: https://readthedocs.org/projects/requests-mock-flask/badge/?version=latest
   :target: https://requests-mock-flask.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |PyPI| image:: https://badge.fury.io/py/requests-mock-flask.svg
   :target: https://badge.fury.io/py/requests-mock-flask
.. |minimum-python-version| replace:: 3.12
