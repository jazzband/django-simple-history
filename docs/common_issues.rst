Common Issues
=============

Bulk Creating and Queryset Updating
-----------------------------------
``django-simple-history`` functions by saving history using a ``post_save`` signal
every time that an object with history is saved. However, for certain bulk
operations, such as bulk_create_ and `queryset updates <https://docs.djangoproject.com/en/2.0/ref/models/querysets/#update>`_,
signals are not sent, and the history is not saved automatically. However,
``django-simple-history`` provides utility functions to work around this.

Bulk Creating a Model with History
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As of ``django-simple-history`` 2.2.0, we can use the utility function
``bulk_create_with_history`` in order to bulk create objects while saving their
history:

.. _bulk_create: https://docs.djangoproject.com/en/2.0/ref/models/querysets/#bulk-create


.. code-block:: pycon

    >>> from simple_history.utils import bulk_create_with_history
    >>> from simple_history.tests.models import Poll
    >>> from django.utils.timezone import now
    >>>
    >>> data = [Poll(id=x, question='Question ' + str(x), pub_date=now()) for x in range(1000)]
    >>> objs = bulk_create_with_history(data, Poll, batch_size=500)
    >>> Poll.objects.count()
    1000
    >>> Poll.history.count()
    1000

If you want to specify a change reason for each record in the bulk create, you
can add `changeReason` on each instance:

.. code-block:: pycon

    >>> for poll in data:
            poll.changeReason = 'reason'
    >>> objs = bulk_create_with_history(data, Poll, batch_size=500)
    >>> Poll.history.get(id=data[0].id).history_change_reason
    'reason'


QuerySet Updates with History
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unlike with ``bulk_create``, `queryset updates`_ perform an SQL update query on
the queryset, and never return the actual updated objects (which would be
necessary for the inserts into the historical table). Thus, we tell you that
queryset updates will not save history (since no ``post_save`` signal is sent).
As the Django documentation says::

    If you want to update a bunch of records for a model that has a custom
    ``save()`` method, loop over them and call ``save()``, like this:

.. code-block:: python

    for e in Entry.objects.filter(pub_date__year=2010):
        e.comments_on = False
        e.save()

.. _queryset updates: https://docs.djangoproject.com/en/2.0/ref/models/querysets/#update


Tracking Custom Users
---------------------

-   ``fields.E300``::

        ERRORS:
        custom_user.HistoricalCustomUser.history_user: (fields.E300) Field defines a relation with model 'custom_user.CustomUser', which is either not installed, or is abstract.

    Use ``register()`` to track changes to the custom user model
    instead of setting ``HistoricalRecords`` on the model directly.
    See :ref:`register`.

    The reason for this, is that unfortunately ``HistoricalRecords``
    cannot be set directly on a swapped user model because of the user
    foreign key to track the user making changes.

Using django-webtest with Middleware
------------------------------------

When using django-webtest_ to test your Django project with the
django-simple-history middleware, you may run into an error similar to the
following::

    django.db.utils.IntegrityError: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`test_env`.`core_historicaladdress`, CONSTRAINT `core_historicaladdress_history_user_id_0f2bed02_fk_user_user_id` FOREIGN KEY (`history_user_id`) REFERENCES `user_user` (`id`))')

.. _django-webtest: https://github.com/django-webtest/django-webtest

This error occurs because ``django-webtest`` sets
``DEBUG_PROPAGATE_EXCEPTIONS`` to true preventing the middleware from cleaning
up the request. To solve this issue, add the following code to any
``clean_environment`` or ``tearDown`` method that
you use:

.. code-block:: python

    from simple_history.middleware import HistoricalRecords
    if hasattr(HistoricalRecords.thread, 'request'):
        del HistoricalRecords.thread.request

Using F() expressions
---------------------
``F()`` expressions, as described here_, do not work on models that have
history. Simple history inserts a new record in the historical table for any
model being updated. However, ``F()`` expressions are only functional on updates.
Thus, when an ``F()`` expression is used on a model with a history table, the
historical model tries to insert using the ``F()`` expression, and raises a
``ValueError``.

.. _here: https://docs.djangoproject.com/en/2.0/ref/models/expressions/#f-expressions


Reserved Field Names
--------------------

For each base model that has its history tracked using ``django-simple-history``,
an associated historical model is created. Thus, if we have:

.. code-block:: python

    class BaseModel(models.Model):
        history = HistoricalRecords()

a Django model called ``HistoricalBaseModel`` is also created with all of the fields
from ``BaseModel``, plus a few extra fields and methods that are on all historical models.

Since these fields and methods are on all historical models, any field or method names
on a base model that clash with those names will not be on the historical model (and,
thus, won't be tracked). The reserved historical field and method names are below:

- ``history_id``
- ``history_date``
- ``history_change_reason``
- ``history_type``
- ``history_object``
- ``history_user``
- ``history_user_id``
- ``instance``
- ``instance_type``
- ``next_record``
- ``prev_record``
- ``revert_url``
- ``__str__``

So if we have:

.. code-block:: python

    class BaseModel(models.Model):
        instance = models.CharField(max_length=255)
        history = HistoricalRecords()

the ``instance`` field will not actually be tracked on the history table because it's
in the reserved set of terms.

Multi-table Inheritance
-----------------------

``django-simple-history`` supports tracking history on models that use multi-table
inheritance, such as:

.. code-block:: python

    class ParentModel(models.Model):
        parent_field = models.CharField(max_length=255)
        history = HistoricalRecords()

    class ChildModel(ParentModel):
        child_field = models.CharField(max_length=255)
        history = HistoricalRecords()


A few notes:

- On the child model, the ``HistoricalRecords`` instance is not inherited from the parent
  model. This means that you can choose to track changes on just the parent model, just
  the child model, or both.
- The child's history table contains all fields from the child model as well as all the
  fields from the parent model.
- Updating a child instance only updates the child's history table, not the parent's
  history table.


Usage with django-modeltranslation
----------------------------------

If you have ``django-modeltranslation`` installed, you will need to use the ``register()``
method to model translation, as described `here <https://github.com/treyhunner/django-simple-history/issues/209#issuecomment-181676111>`__.


Pointing to the model
---------------------

Sometimes you have to point to the model of the historical records. Examples are Django's generic views or Django REST framework's serializers. You can get there through your HistoricalRecords manager you defined in your model. According to our example:

.. code-block:: python

    class PollHistoryListView(ListView): # or PollHistorySerializer(ModelSerializer):
        class Meta:
            model = Poll.history.model
           # ...

Working with BitBucket Pipelines
--------------------------------

When using BitBucket Pipelines to test your Django project with the
django-simple-history middleware, you will run into an error relating to missing migrations relating to the historic User model from the auth app. This is because the migration file is not held within either your project or django-simple-history.  In order to pypass the error you need to add a ```python manage.py makemigrations auth``` step into your YML file prior to running the tests.
