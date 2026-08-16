Changelog
=========

.. towncrier release notes start

2026.08.16
----------

- Use ``types-httpretty`` to type-check the HTTPretty integration.

- Escape regex meta-characters in literal URL components.

- Preserve binary response bodies when using the ``requests_mock`` back end.

- The intercepted request host and scheme are now preserved when forwarding to the Flask app.

- Repeated response headers such as ``Set-Cookie`` and ``Warning`` are now preserved by the ``responses`` and ``requests_mock`` back ends instead of being collapsed to a single value.

- Route patterns are now anchored so that a rule such as ``/api`` no longer intercepts unrelated paths such as ``/api-extra``, while still matching an optional query string.

- Path prefixes supplied in ``base_url`` are now preserved when registering Flask routes.

- Requests using an unsupported method for a known route are now forwarded to Flask, which returns its usual ``405 Method Not Allowed`` response.

- Requests to the form without a trailing slash of a slash-terminated Flask route are now forwarded so that Flask can produce its trailing-slash redirect.

- Percent-encode the static portions of route paths so that non-ASCII routes such as ``/café`` are reachable through the mock.

- Custom framework converters that set ``part_isolating = False`` now correctly match values containing slashes.

- The scheme and host of ``base_url`` are now normalized to lowercase so that requests to case-insensitive URL components are intercepted.

- Duplicate request cookies with the same name are now preserved instead of being collapsed to the last value.

- Forward the original ``Cookie`` header verbatim so valueless cookie tokens are preserved in forwarded requests.

- Forward the original ``Cookie`` header to Flask instead of re-parsing it, so requests with cookie names that the framework accepts but ``SimpleCookie`` rejects no longer crash.

- Support iterable streaming request bodies with the ``responses`` and ``requests-mock`` backends.

- Custom HTTP reason phrases from Flask responses are now preserved for the ``requests_mock`` back end.

- Prevent HTTPretty from crashing on nonstandard Flask status codes.

- URL interception now honors Flask converter constraints, so requests that violate a route's converter (for example a non-integer where ``<int:...>`` is expected) are left unmatched instead of being forwarded.

- Host-constrained Flask rules are now only registered against a ``base_url`` whose host matches the rule's host.

- Internationalized ``base_url`` host names are now normalized to their IDNA form so that internationalized routes are intercepted.

- Forwarded Flask responses are now closed so ``call_on_close`` callbacks run.

- Custom converter arguments containing a quoted ``>`` are no longer truncated when generating URL patterns, so applications that use them can be attached to a mock back end.

2026.04.02
----------


2026.02.16
----------


* Add support for ``respx``.

2026.01.12
----------


* Fix a bug where routes with multiple variables (e.g. ``/users/<org>/<user>/posts``) would incorrectly match URLs with extra path segments.

2025.01.13
----------

* Add requirements for ``httpretty``, ``requests-mock`` and ``responses``.
* Add more type safety for the passed in mock object.

2024.08.30.1
------------

2024.08.30
------------

2023.05.14
------------

2023.03.05.1
------------

2023.03.05
------------

2022.04.03
------------

2021.12.28.1
------------

Add support for ``httpretty``.

2021.12.28
------------

Remove ``Flask``, ``requests`` and ``requests_mock`` as dependencies.

2021.12.13
------------

2021.07.10.0
------------

Support Flask 2 and greater.
Drop support for Flask < 2.
Please use an older version of this package if you wish to use an older version of Flask.

2020.09.25.0
------------

2020.09.18.0
------------

2020.09.16.0
------------

2020.09.14.1
------------

2020.09.14.0
------------

2020.01.20.2
------------

2020.01.20.1
------------

2020.01.20.0
------------
