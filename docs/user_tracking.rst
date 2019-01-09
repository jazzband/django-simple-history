User Tracking
=============


Recording Which User Changed a Model
------------------------------------
There are three documented ways to attach users to a tracked change:

1. Use the ``HistoryRequestMiddleware``. The middleware sets the
User instance that made the request as the ``history_user`` on the history
table.

2. Use ``simple_history.admin.SimpleHistoryAdmin``. Under the hood,
``SimpleHistoryAdmin`` actually sets the ``_history_user`` on the object to
attach the user to the tracked change by overriding the `save_model` method.

3. Assign a user to the ``_history_user`` attribute of the object as described
below:

Using ``_history_user`` to Record Which User Changed a Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Admin integration requires that you use a ``_history_user.setter`` attribute with
your custom ``_history_user`` property (see :doc:`/admin`).

Another option for identifying the change user is by providing a function via ``get_user``.
If provided it will be called everytime that the ``history_user`` needs to be
identified with the following key word arguments:

* ``instance``:  The current instance being modified
* ``request``:  If using the middleware the current request object will be provided if they are authenticated.

This is very helpful when using ``register``:

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        changed_by = models.ForeignKey('auth.User')


    def get_poll_user(instance, **kwargs):
        return instance.changed_by

    register(Poll, get_user=get_poll_user)


Change User Model
------------------------------------

If you need to use a different user model then ``settings.AUTH_USER_MODEL``,
pass in the required model to ``user_model``.  Doing this requires ``_history_user``
or ``get_user`` is provided as detailed above.

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class PollUser(models.Model):
        user_id = models.ForeignKey('auth.User')


    # Only PollUsers should be modifying a Poll
    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        changed_by = models.ForeignKey(PollUser)
        history = HistoricalRecords(user_model=PollUser)

        @property
        def _history_user(self):
            return self.changed_by

        @_history_user.setter
        def _history_user(self, value):
            self.changed_by = value
