Quick Start
===========

Install
-------

This package is available on `PyPI`_ and `Crate.io`_.

Install from PyPI with ``pip``:

.. code-block:: bash

    $ pip install django-simple-history

.. _pypi: https://pypi.python.org/pypi/django-simple-history/
.. _crate.io: https://crate.io/packages/django-simple-history/


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
the user making the change as documented in :doc:`/advanced`.

Models
~~~~~~

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

Existing Projects
~~~~~~~~~~~~~~~~~

For existing projects, you can call the populate command to generate an
initial change for preexisting model instances:

.. code-block:: bash

    $ python manage.py populate_history --auto

.. _admin_integration:

Integration with Django Admin
-----------------------------

To allow viewing previous model versions on the Django admin site, inherit from
the ``simple_history.admin.SimpleHistoryAdmin`` class when registering your
model with the admin site.

This will replace the history object page on the admin site and allow viewing
and reverting to previous model versions.  Changes made in admin change forms
will also accurately note the user who made the change.

.. image:: screens/1_poll_history.png

Clicking on an object presents the option to revert to that version of the object.

.. image:: screens/2_revert.png

(The object is reverted to the selected state)

.. image:: screens/3_poll_reverted.png

Reversions like this are added to the history.

.. image:: screens/4_history_after_poll_reverted.png

An example of admin integration for the ``Poll`` and ``Choice`` models:

.. code-block:: python

    from django.contrib import admin
    from simple_history.admin import SimpleHistoryAdmin
    from .models import Poll, Choice

    admin.site.register(Poll, SimpleHistoryAdmin)
    admin.site.register(Choice, SimpleHistoryAdmin)

Changing a history-tracked model from the admin interface will automatically record the user who made the change (see :doc:`/advanced`).


Querying history
----------------

Querying history on a model instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``HistoricalRecords`` object on a model instance can be used in the same
way as a model manager:

.. code-block:: pycon

    >>> from polls.models import Poll, Choice
    >>> from datetime import datetime
    >>> poll = Poll.objects.create(question="what's up?", pub_date=datetime.now())
    >>>
    >>> poll.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

Whenever a model instance is saved a new historical record is created:

.. code-block:: pycon

    >>> poll.pub_date = datetime(2007, 4, 1, 0, 0)
    >>> poll.save()
    >>> poll.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>, <HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

Querying history on a model class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Historical records for all instances of a model can be queried by using the
``HistoricalRecords`` manager on the model class.  For example historical
records for all ``Choice`` instances can be queried by using the manager on the
``Choice`` model class:

.. code-block:: pycon

    >>> choice1 = poll.choice_set.create(choice_text='Not Much', votes=0)
    >>> choice2 = poll.choice_set.create(choice_text='The sky', votes=0)
    >>>
    >>> Choice.history
    <simple_history.manager.HistoryManager object at 0x1cc4290>
    >>> Choice.history.all()
    [<HistoricalChoice: Choice object as of 2010-10-25 18:05:12.183340>, <HistoricalChoice: Choice object as of 2010-10-25 18:04:59.047351>]

Because the history is model, you can also filter it like regularly QuerySets,
a.k. Choice.history.filter(choice_text='Not Much') will work!
