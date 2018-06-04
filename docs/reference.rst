Common Issues
=============

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
``DEBUG_PROPOGATE_EXCEPTIONS`` to true preventing the middleware from cleaning
up the request. To solve this issue, add the following code to any
``clean_environment`` or ``tearDown`` method that
you use:

.. code-block::python

    from simple_history.middleware import HistoricalRecords
    if hasattr(HistoricalRecords.thread, 'request'):
        del HistoricalRecords.thread.request
