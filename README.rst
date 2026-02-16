|Build Status| |PyPI|

requests-mock-flask
===================

``requests-mock-flask`` helps with testing `Flask`_ applications with `httpretty`_, `respx`_, `responses`_ or `requests-mock`_.

.. contents::
   :local:

Installation
------------

Requires Python |minimum-python-version|\+.

.. code-block:: sh

   pip install requests-mock-flask


Usage examples
--------------

.. code-block:: python

   """Examples of using requests-mock-flask."""

   from http import HTTPStatus

   import flask
   import httpretty  # pyright: ignore[reportMissingTypeStubs]
   import httpx
   import requests
   import requests_mock
   import responses
   import respx

   from requests_mock_flask import add_flask_app_to_mock

   app = flask.Flask(import_name="example_app")


   @app.route(rule="/")
   def _() -> str:
       """Return a simple message."""
       return "Hello, World!"


   # Using responses
   with responses.RequestsMock(assert_all_requests_are_fired=False) as resp_m:
       add_flask_app_to_mock(
           mock_obj=resp_m,
           flask_app=app,
           base_url="http://www.example.com",
       )

       response = requests.get(url="http://www.example.com", timeout=30)

   assert response.status_code == HTTPStatus.OK
   assert response.text == "Hello, World!"


   # Using requests-mock
   with requests_mock.Mocker() as req_m:
       add_flask_app_to_mock(
           mock_obj=req_m,
           flask_app=app,
           base_url="http://www.example.com",
       )

       response = requests.get(url="http://www.example.com", timeout=30)

   assert response.status_code == HTTPStatus.OK
   assert response.text == "Hello, World!"


   # Using a requests-mock adapter
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


   # Using httpretty
   with httpretty.core.httprettized():  # type: ignore[no-untyped-call]
       add_flask_app_to_mock(
           mock_obj=httpretty,
           flask_app=app,
           base_url="http://www.example.com",
       )

       response = requests.get(url="http://www.example.com", timeout=30)

   assert response.status_code == HTTPStatus.OK
   assert response.text == "Hello, World!"


   # Using respx
   with respx.mock() as respx_mock:
       add_flask_app_to_mock(
           mock_obj=respx_mock,
           flask_app=app,
           base_url="http://www.example.com",
       )

       httpx_response = httpx.get(url="http://www.example.com")

   assert httpx_response.status_code == HTTPStatus.OK
   assert httpx_response.text == "Hello, World!"

Use cases
---------

* Use ``requests`` or other Python APIs for testing Flask applications.
* Create a test suite which can test a Flask application as well as a live web application, to make a verified fake.
* Test a service which calls a Flask application that you have the source code for.


Full documentation
------------------

See the `full documentation <https://adamtheturtle.github.io/requests-mock-flask/>`__ for more information including how to contribute.

.. _Flask: https://flask.palletsprojects.com/
.. _requests-mock: https://requests-mock.readthedocs.io/en/latest/
.. _respx: https://lundberg.github.io/respx/
.. _responses: https://github.com/getsentry/responses
.. _httpretty: https://httpretty.readthedocs.io

.. |Build Status| image:: https://github.com/adamtheturtle/requests-mock-flask/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/adamtheturtle/requests-mock-flask/actions
.. |PyPI| image:: https://badge.fury.io/py/requests-mock-flask.svg
   :target: https://badge.fury.io/py/requests-mock-flask
.. |minimum-python-version| replace:: 3.12
