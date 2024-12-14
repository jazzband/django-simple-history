Contributing to django-simple-history
=====================================

By contributing you agree to abide by the `Contributor Code of Conduct <https://github.com/django-commons/django-simple-history/blob/master/CODE_OF_CONDUCT.md>`_.

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
  and Python as well as running tasks like lint, format, docs
- `coverage`_: used for analyzing test coverage for tests

If not using a virtualenv, the command should be prepended with ``sudo``.

.. _tox: http://testrun.org/tox/latest//
.. _coverage: http://nedbatchelder.com/code/coverage/

Documentation
-------------

To regenerate the documentation run::

    make docs

Testing
-------

Please add tests for your pull requests and make sure your changes don't break
existing tests.

To run tox and generate an HTML code coverage report (available in the
``htmlcov`` directory)::

    make test

To quickly run the tests against a single version of Python and Django (note: you must
``pip install django`` beforehand)::

    python runtests.py

Code Formatting
---------------
We make use of `black`_ for code formatting.

.. _black: https://black.readthedocs.io/en/stable/installation_and_usage.html

You can install and run it along with other linters through pre-commit::

    pre-commit install
    pre-commit run

Once you install pre-commit it will sanity check any commit you make.
Additionally, the CI process runs this check as well.

Translations
------------

In order to add translations, refer to Django's `translation docs`_ and follow these
steps:

1. Ensure that Django is installed
2. Invoke ``django-admin makemessages -l <LOCALE NAME>`` in the repository's root
   directory.
3. Add translations to the created
   ``simple_history/locale/<LOCALE NAME>/LC_MESSAGES/django.po`` file.
4. Compile these with ``django-admin compilemessages``.
5. Commit and publish your translations as described above.

.. _translation docs: https://docs.djangoproject.com/en/stable/topics/i18n/translation/#localization-how-to-create-language-files
