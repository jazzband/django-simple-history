Multiple databases
==================
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
