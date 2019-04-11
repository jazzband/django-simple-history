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

Migrating Historical Tables to Multiple Databases
-------------------------------------------------
If you want your historical records to live in separate databases, you will need
to write a [database router](https://docs.djangoproject.com/en/2.1/topics/db/multi-db/#database-routers).
The router interface requires 4 methods, but the only one that concerns us here
is `allow_migrate`:
```
class DbRouter(object):
    ...
    def allow_migrate(self, db, app_label, model_name, **kwargs):
        if self._is_history_db(db, app_label, model_name, kwargs):
            return True
        elif self._is_default_db(db, app_label, model_name, kwargs):
            return True
        else:
            return False
```
Your `_is_history_db` method can be implemented however you like.

Tracking History in a Separate Database
---------------------------------------
If you want to manage a historical model in separate database from its
operational model, you may pass the `using` keyword to the `HistoricalRecords`
constructor:
```
class MyModel(models.Model):
    ...
    history = HistoricalRecords(using='history_db')
```

As long as your historical table has been migrated to the `history_db`, you will
be able to write to that database on every history event.

## Testing
If you wish to test the existence of historical models in separate databases,
you will need to add a Meta inner class:

```
class ModelWithHistoryInDifferentDb(models.Model):
    name = models.CharField(max_length=30)
    history = HistoricalRecords(using="other")

    class Meta:
        app_label = "external"
```

The app_label must be set to "external" for the migration to apply to the test database.