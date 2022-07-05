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
history user automatically you can add ``HistoryRequestMiddleware`` to your Django
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

Track History for a Third-Party Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To track history for a model you didn't create, use the
``simple_history.register`` function.  You can use this to track models from
third-party apps you don't have control over.  Here's an example of using
``simple_history.register`` to history-track the ``User`` model from the
``django.contrib.auth`` app:

.. code-block:: python

    from simple_history import register
    from django.contrib.auth.models import User

    register(User)

If you want to separate the migrations of the historical model into an app other than
the third-party model's app, you can set the ``app`` parameter in
``register``. For instance, if you want the migrations to live in the migrations
folder of the package you register the model in, you could do:

.. code-block:: python

    register(User, app=__package__)


Run Migrations
--------------

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

What Now?
---------

By adding ``HistoricalRecords`` to a model or registering a model using ``register``,
you automatically start tracking any create, update, or delete that occurs on that model.
Now you can :doc:`query the history programmatically </querying_history>`
and :doc:`view the history in Django admin </admin>`.

What is ``django-simple-history`` Doing Behind the Scenes?
----------------------------------------------------------

If you tried the code `above`_ and ran the migrations on it, you'll see the following
tables in your database:

- ``app_choice``
- ``app_historicalchoice``
- ``app_historicalpoll``
- ``app_poll``

.. _above: `Track History`_

The two extra tables with ``historical`` prepend to their names are tables created
by ``django-simple-history``. These tables store every change that you make to their
respective base tables. Every time a create, update, or delete occurs on ``Choice`` or
``Poll`` a new row is created in the historical table for that model including all of
the fields in the instance of the base model, as well as other metadata:

- ``history_user``: the user that made the create/update/delete
- ``history_date``: the ``datetime`` at which the create/update/delete occurred
- ``history_change_reason``: the reason the create/update/delete occurred (null by default)
- ``history_id``: the primary key for the historical table (note the base table's
  primary key is not unique on the historical table since there are multiple versions of it
  on the historical table)
- ``history_type``: ``+`` for create, ``~`` for update, and ``-`` for delete


Now try saving an instance of ``Choice`` or ``Poll``. Check the historical table
to see that the history is being tracked.
