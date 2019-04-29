Multiple databases
==================

Interacting with Multiple Databases
-----------------------------------

`django-simple-history` follows the Django conventions for interacting with multiple databases.

.. code-block:: python

    >>> # This will create a new historical record on the 'other' database.
    >>> poll = Poll.objects.using('other').create(question='Question 1')

    >>> # This will also create a new historical record on the 'other' database.
    >>> poll.save(using='other')


When interacting with ``QuerySets``, use ``using()``:

.. code-block:: python

    >>> # This will return a QuerySet from the 'other' database.
    Poll.history.using('other').all()

When interacting with manager methods, use ``db_manager()``:

.. code-block:: python

    >>> # This will call a manager method on the 'other' database.
    >>> poll.history.db_manager('other').as_of(datetime(2010, 10, 25, 18, 4, 0))

See the Django documentation for more information on how to interact with multiple databases.

Tracking User in a Separate Database
------------------------------------

When using ``django-simple-history`` in app with multiple database, you may run into
an issue where you want to track the history on a table that lives in a separate
database to your user model. Since Django does not support cross-database relations,
you will have to manually track the ``history_user`` using an explicit ID. The full
documentation on this feature is in :ref:`Manually Track User Model`.

Tracking History Separate from the Base Model
---------------------------------------------
You can choose whether or not to track models' history in the same database by
setting the flag `use_base_model_db`.

.. code-block:: python

    class MyModel(models.Model):
        ...
        history = HistoricalRecords(use_base_model_db=False)

If set to `True`, migrations and audit
events will be sent to the same database as the base model. If `False`, they
will be sent to the place specified by the database router. The default value is `False`.
