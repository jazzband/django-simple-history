Common Issues
=============

-   ``fields.E300``::

        ERRORS:
        custom_user.HistoricalCustomUser.history_user: (fields.E300) Field defines a relation with model 'custom_user.CustomUser', which is either not installed, or is abstract.

    Use ``register()`` to track changes to the custom user model
    instead of setting ``HistoricalRecords`` on the model directly.
    See :ref:`register`.

    The reason for this, is that unfortunately ``HistoricalRecords``
    cannot be set directly on a swapped user model because of the user
    foreign key to track the user making changes.
