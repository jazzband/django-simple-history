django-simple-history
=====================

.. image:: https://github.com/django-commons/django-simple-history/actions/workflows/test.yml/badge.svg
   :target: https://github.com/django-commons/django-simple-history/actions/workflows/test.yml
   :alt: Build Status

.. image:: https://readthedocs.org/projects/django-simple-history/badge/?version=latest
   :target: https://django-simple-history.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/codecov/c/github/django-commons/django-simple-history/master.svg
   :target: https://app.codecov.io/github/django-commons/django-simple-history?branch=master
   :alt: Test Coverage

.. image:: https://img.shields.io/pypi/v/django-simple-history.svg
   :target: https://pypi.org/project/django-simple-history/
   :alt: PyPI Version

.. image:: https://api.codeclimate.com/v1/badges/66cfd94e2db991f2d28a/maintainability
   :target: https://codeclimate.com/github/django-commons/django-simple-history/maintainability
   :alt: Maintainability

.. image:: https://static.pepy.tech/badge/django-simple-history
   :target: https://pepy.tech/project/django-simple-history
   :alt: Downloads

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style


django-simple-history stores Django model state on every create/update/delete.

This app supports the following combinations of Django and Python:

==========  =======================
  Django      Python
==========  =======================
4.2         3.9, 3.10, 3.11, 3.12, 3.13
5.0         3.10, 3.11, 3.12, 3.13
5.1         3.10, 3.11, 3.12, 3.13
main        3.10, 3.11, 3.12, 3.13
==========  =======================

Contribute
----------

- Issue Tracker: https://github.com/django-commons/django-simple-history/issues
- Source Code: https://github.com/django-commons/django-simple-history

Pull requests are welcome.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   quick_start
   querying_history
   admin
   historical_model
   user_tracking
   signals
   history_diffing
   multiple_dbs
   utils
   common_issues


.. include:: ../CHANGES.rst
