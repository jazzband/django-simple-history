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

-   ``HistoricalRecords`` is not inherited

    Allowing ``HistoricalRecords`` to be inherited from abstract
    models or other parents is a feature we would love to add. The
    current contributors do not have a need for that feature at this
    point, and need some help understanding how this feature should be
    completed. Current work is in `#112`__.

    __ https://github.com/treyhunner/django-simple-history/pull/112
