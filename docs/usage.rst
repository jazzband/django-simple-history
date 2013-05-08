Usage
=====

Install
-------

This package is available on `PyPI`_ and `Crate.io`_.

Install from PyPI with ``pip``:

.. code-block:: bash

    $ pip install django-simple-history

.. _pypi: https://pypi.python.org/pypi/django-simple-history/
.. _crate.io: https://crate.io/packages/django-simple-history/


Quickstart
----------

To track history for a model, create an instance of
``simple_history.models.HistoricalRecords`` on the model.

An example for tracking changes on the ``Poll`` and ``Choice`` models in the
Django tutorial:

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        history = HistoricalRecords()

    class Choice(models.Model):
        poll = models.ForeignKey(Poll)
        choice_text = models.CharField(max_length=200)
        votes = models.IntegerField(default=0)
        history = HistoricalRecords()

Now all changes to ``Poll`` and ``Choice`` model instances will be tracked in
the database.


Integration with Django Admin
-----------------------------

To allow viewing previous model versions on the Django admin site, inherit from
the ``simple_history.admin.SimpleHistoryAdmin`` class when registering your
model with the admin site.

This will replace the history object page on the admin site and allow viewing
and reverting to previous model versions.  Changes made in admin change forms
will also accurately note the user who made the change.

An example of admin integration for the ``Poll`` and ``Choice`` models:

.. code-block:: python

    from django.contrib import admin
    from simple_history.admin import SimpleHistoryAdmin
    from .models import Poll, Choice

    admin.site.register(Poll, SimpleHistoryAdmin)
    admin.site.register(Choice, SimpleHistoryAdmin)
