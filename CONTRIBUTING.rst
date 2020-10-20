Contributing to django-simple-history
=====================================

.. image:: https://jazzband.co/static/img/jazzband.svg
   :target: https://jazzband.co/
   :alt: Jazzband

This is a `Jazzband <https://jazzband.co>`_ project. By contributing you agree to abide by the `Contributor Code of Conduct <https://jazzband.co/about/conduct>`_ and follow the `guidelines <https://jazzband.co/about/guidelines>`_.

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

Once it is installed you can make sure the code is properly formatted by running::

    make format

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

.. _translation docs: https://docs.djangoproject.com/en/dev/topics/i18n/translation/#localization-how-to-create-language-files
