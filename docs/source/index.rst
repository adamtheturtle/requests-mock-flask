|project|
=========

|project| helps with testing `Flask`_ applications with `httpretty`_, `respx`_ (for `httpx`_ and `HTTPX2`_), `responses`_ or `requests-mock`_.

Installation
------------

Requires Python |minimum-python-version|\+.

.. code-block:: shell

   pip install requests-mock-flask


Usage examples
--------------

.. code-block:: python

   """Examples of using requests-mock-flask."""

   from http import HTTPStatus

   import flask
   import httpretty
   import httpx
   import httpx2
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
   with httpretty.core.httprettized():
       add_flask_app_to_mock(
           mock_obj=httpretty,
           flask_app=app,
           base_url="http://www.example.com",
       )

       response = requests.get(url="http://www.example.com", timeout=30)

   assert response.status_code == HTTPStatus.OK
   assert response.text == "Hello, World!"


   # Using respx
   with respx.mock(assert_all_called=False) as respx_mock:
       add_flask_app_to_mock(
           mock_obj=respx_mock,
           flask_app=app,
           base_url="http://www.example.com",
       )

       httpx_response = httpx.get(url="http://www.example.com")

   assert httpx_response.status_code == HTTPStatus.OK
   assert httpx_response.text == "Hello, World!"


   # Using respx with httpx2
   #
   # ``pytest-httpx2`` registers the ``httpcore2`` mocker with ``respx``.
   # It is loaded automatically under pytest; import it elsewhere.
   with respx.mock(assert_all_called=False, using="httpcore2") as respx_mock:
       add_flask_app_to_mock(
           mock_obj=respx_mock,
           flask_app=app,
           base_url="http://www.example.com",
       )

       httpx2_response = httpx2.get(url="http://www.example.com")

   assert httpx2_response.status_code == HTTPStatus.OK
   assert httpx2_response.text == "Hello, World!"

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
   unreleased
   changelog
   contributing

.. _Flask: https://flask.palletsprojects.com/
.. _httpx: https://www.python-httpx.org/
.. _HTTPX2: https://httpx2.pydantic.dev/
.. _httpretty: https://httpretty.readthedocs.io
.. _requests-mock: https://requests-mock.readthedocs.io/en/latest/
.. _respx: https://lundberg.github.io/respx/
.. _responses: https://github.com/getsentry/responses
