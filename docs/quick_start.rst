Quick Start
===========

Install
-------

Install from `PyPI`_ with ``pip``:

.. code-block:: bash

    $ pip install django-simple-history

.. _pypi: https://pypi.python.org/pypi/django-simple-history/


Configure
---------

Settings
~~~~~~~~

Add ``simple_history`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'simple_history',
    ]

The historical models can track who made each change. To populate the
history user automatically you can add middleware to your Django
settings:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'simple_history.middleware.HistoryRequestMiddleware',
    ]

If you do not want to use the middleware, you can explicitly indicate
the user making the change as documented in :doc:`/user_tracking`.

Track History
~~~~~~~~~~~~~

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

Run Migrations
~~~~~~~~~~~~~~

With your model changes in place, create and apply the database migrations:

.. code-block:: bash

    $ python manage.py makemigrations
    $ python manage.py migrate

Existing Projects
~~~~~~~~~~~~~~~~~

For existing projects, you can call the populate command to generate an
initial change for preexisting model instances:

.. code-block:: bash

    $ python manage.py populate_history --auto

By default, history rows are inserted in batches of 200. This can be changed if needed for large tables
by using the ``--batchsize`` option, for example ``--batchsize 500``.
