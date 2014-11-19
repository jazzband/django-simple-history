Advanced Usage
==============

Database Migrations
-------------------

By default, Historical models live in the same app as the model they
track. Historical models are tracked by migrations in the same way as
any other model. Whenever the original model changes, the historical
model will change also.

Therefore tracking historical models with migrations should work
automatically.


Locating past model instance
----------------------------

Two extra methods are provided for locating previous models instances on
historical record model managers.

as_of
~~~~~

This method will return an instance of the model as it would have existed at
the provided date and time.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> poll.history.as_of(datetime(2010, 10, 25, 18, 4, 0))
    <Poll: Poll object as of 2010-10-25 18:03:29.855689>
    >>> poll.history.as_of(datetime(2010, 10, 25, 18, 5, 0))
    <Poll: Poll object as of 2010-10-25 18:04:13.814128>

most_recent
~~~~~~~~~~~

This method will return the most recent copy of the model available in the
model history.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> poll.history.most_recent()
    <Poll: Poll object as of 2010-10-25 18:04:13.814128>


.. _register:

History for a Third-Party Model
-------------------------------

To track history for a model you didn't create, use the
``simple_history.register`` utility.  You can use this to track models from
third-party apps you don't have control over.  Here's an example of using
``simple_history.register`` to history-track the ``User`` model from the
``django.contrib.auth`` app:

.. code-block:: python

    from simple_history import register
    from django.contrib.auth.models import User

    register(User)


.. recording_user:

Recording Which User Changed a Model
------------------------------------

To denote which user changed a model, assign a ``_history_user`` attribute on
your model.

For example if you have a ``changed_by`` field on your model that records which
user last changed the model, you could create a ``_history_user`` property
referencing the ``changed_by`` field:

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        changed_by = models.ForeignKey('auth.User')
        history = HistoricalRecords()

        @property
        def _history_user(self):
            return self.changed_by

        @_history_user.setter
        def _history_user(self, value):
            self.changed_by = value

Admin integration requires that you use a ``_history_user.setter`` attribute with your custom ``_history_user`` property (see :ref:`admin_integration`).


Custom ``history_date``
-----------------------

You're able to set a custom ``history_date`` attribute for the historical
record, by defining the property ``_history_date`` in your model. That's
helpful if you want to add versions to your model, which happened before the
current model version, e.g. when batch importing historical data. The content
of the property ``_history_date`` has to be a datetime-object, but setting the
value of the property to a ``DateTimeField``, which is already defined in the
model, will work too.

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        changed_by = models.ForeignKey('auth.User')
        history = HistoricalRecords()
        __history_date = None

        @property
        def _history_date(self):
            return self.__history_date

        @_history_date.setter
        def _history_date(self, value):
            self.__history_date = value

.. code-block:: python

    from datetime import datetime
    from models import Poll

    my_poll = Poll(question="what's up?")
    my_poll._history_date = datetime.now()
    my_poll.save()


Change Base Class of HistoricalRecord Models
--------------------------------------------

To change the auto-generated HistoricalRecord models base class from
``models.Model``, pass in the abstract class in a list to ``bases``.

.. code-block:: python

    class RoutableModel(models.Model):
        class Meta:
            abstract = True


    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        changed_by = models.ForeignKey('auth.User')
        history = HistoricalRecords(bases=[RoutableModel])
