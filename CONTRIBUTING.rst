Contributing to django-simple-history
=====================================

Pull Requests
-------------

Feel free to open pull requests before you've finished your code or tests.
Opening your pull request soon will allow others to comment on it sooner.

A checklist of things to remember when making a feature:

- Write tests if applicable
- Note important changes in the `CHANGES`_ file
- Update the `README`_ file if needed
- Update the documentation if needed
- Add yourself to the `AUTHORS`_ file

.. _AUTHORS: AUTHORS.rst
.. _CHANGES: CHANGES.rst
.. _README: README.rst

Requirements
------------

The Makefile can be used for generating documentation and running tests.

To install the requirements necessary for generating the documentation and
running tests::

    make init

This will install:

- `tox`_: used for running the tests against all supported versions of Django
  and Python
- `coverage`_: used for analyzing test coverage for tests
- `Sphinx`_: used for generating documentation

If not using a virtualenv, the command should be prepended with ``sudo``.

.. _tox: http://testrun.org/tox/latest//
.. _coverage: http://nedbatchelder.com/code/coverage/
.. _sphinx: http://sphinx-doc.org/

Documentation
-------------

To regenate the documentation run::

    make docs

Testing
-------

Please add tests for your pull requests and make sure your changes don't break
existing tests.

To run tox and generate an HTML code coverage report (available in the
``htmlcov`` directory)::

    make test

To quickly run the tests against a single version of Python and Django::

    python setup.py test
