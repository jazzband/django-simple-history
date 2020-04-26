Historical Model Customizations
===============================

Custom ``history_id``
---------------------
By default, the historical table of a model will use an ``AutoField`` for the table's
``history_id`` (the history table's primary key). However, you can specify a different
type of field for ``history_id`` by passing a different field to ``history_id_field``
parameter.

The example below uses a ``UUIDField`` instead of an ``AutoField``:


.. code-block:: python

    import uuid
    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        history = HistoricalRecords(
            history_id_field=models.UUIDField(default=uuid.uuid4)
        )


Since using a ``UUIDField`` for the ``history_id`` is a common use case, there is a
``SIMPLE_HISTORY_HISTORY_ID_USE_UUID`` setting that will set all ``history_id``s to UUIDs.
Set this with the following line in your ``settings.py`` file:


.. code-block:: python

    SIMPLE_HISTORY_HISTORY_ID_USE_UUID = True



This setting can still be overridden using the ``history_id_field`` parameter on a per model basis.

You can use the ``history_id_field`` parameter with both ``HistoricalRecords()`` or
``register()`` to change this behavior.

Note: regardless of what field type you specify as your history_id field, that field will
automatically set ``primary_key=True`` and ``editable=False``.


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


Custom history table name
-------------------------

By default, the table name for historical models follow the Django convention
and just add ``historical`` before model name. For instance, if your application
name is ``polls`` and your model name ``Question``, then the table name will be
``polls_historicalquestion``.

You can use the ``table_name`` parameter with both ``HistoricalRecords()`` or
``register()`` to change this behavior.

.. code-block:: python

    class Question(models.Model):
        question_text = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')
        history = HistoricalRecords(table_name='polls_question_history')

.. code-block:: python

    class Question(models.Model):
        question_text = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

    register(Question, table_name='polls_question_history')


Custom model name
-----------------

By default, historical model is named as 'Historical' + model name. For
example, historical records for ``Choice`` is called ``HistoricalChoice``.
Users can specify a custom model name via the constructor on
``HistoricalRecords``. The common use case for this is avoiding naming conflict
if the user already defined a model named as 'Historical' + model name.

This feature provides the ability to override the default model name used for the generated history model.

To configure history models to use a different name for the history model class, use an option named ``custom_model_name``.
The value for this option can be a `string` or a `callable`.
A simple string replaces the default name of `'Historical' + model name` with the defined string.
The most simple use case is illustrated below using a simple string:

.. code-block:: python

    class ModelNameExample(models.Model):
        history = HistoricalRecords(
            custom_model_name='SimpleHistoricalModelNameExample'
        )

If you are using a base class for your models and want to apply a name change for the historical model
for all models using the base class then a callable can be used.
The callable is passed the name of the model for which the history model will be created.
As an example using the callable mechanism, the below changes the default prefix `Historical` to `Audit`:

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        history = HistoricalRecords(custom_model_name=lambda x:f'Audit{x}')

    class Opinion(models.Model):
        opinion = models.CharField(max_length=2000)

    register(Opinion, custom_model_name=lambda x:f'Audit{x}')

The resulting history class names would be `AuditPoll` and `AuditOpinion`.
If the app the models are defined in is `yoda` then the corresponding history table names would be `yoda_auditpoll` and `yoda_auditopinion`

IMPORTANT: Setting `custom_model_name` to `lambda x:f'{x}'` is not permitted.
           An error will be generated and no history model created if they are the same.


TextField as `history_change_reason`
------------------------------------

The ``HistoricalRecords`` object can be customized to accept a
``TextField`` model field for saving the
`history_change_reason` either through settings or via the constructor on the
model. The common use case for this is for supporting larger model change
histories to support changelog-like features.

.. code-block:: python

    SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD=True

or

.. code-block:: python

    class TextFieldExample(models.Model):
        greeting = models.CharField(max_length=100)
        history = HistoricalRecords(
            history_change_reason_field=models.TextField(null=True)
        )



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


Excluded Fields
--------------------------------

It is possible to use the parameter ``excluded_fields`` to choose which fields
will be stored on every create/update/delete.

For example, if you have the model:

.. code-block:: python

    class PollWithExcludeFields(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

And you don't want to store the changes for the field ``pub_date``, it is necessary to update the model to:

.. code-block:: python

    class PollWithExcludeFields(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

        history = HistoricalRecords(excluded_fields=['pub_date'])

By default, django-simple-history stores the changes for all fields in the model.

Adding additional fields to historical models
---------------------------------------------

Sometimes it is useful to be able to add additional fields to historical models that do not exist on the
source model. This is possible by combining the ``bases`` functionality with the ``pre_create_historical_record`` signal.

.. code-block:: python

    # in models.py
    class IPAddressHistoricalModel(models.Model):
        """
        Abstract model for history models tracking the IP address.
        """
        ip_address = models.GenericIPAddressField(_('IP address'))

        class Meta:
            abstract = True


    class PollWithExtraFields(models.Model):
        question = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

        history = HistoricalRecords(bases=[IPAddressHistoricalModel,])


.. code-block:: python

    # define your signal handler/callback anywhere outside of models.py
    def add_history_ip_address(sender, **kwargs):
        history_instance = kwargs['history_instance']
        # thread.request for use only when the simple_history middleware is on and enabled
        history_instance.ip_address = HistoricalRecords.thread.request.META['REMOTE_ADDR']


.. code-block:: python

    # in apps.py
    class TestsConfig(AppConfig):
        def ready(self):
            from simple_history.tests.models \
                import HistoricalPollWithExtraFields

            pre_create_historical_record.connect(
                add_history_ip_address,
                sender=HistoricalPollWithExtraFields
            )


More information on signals in ``django-simple-history`` is available in :doc:`/signals`.

Change Reason
-------------

Change reason is a message to explain why the change was made in the instance. It is stored in the
field ``history_change_reason`` and its default value is ``None``.

By default, the django-simple-history gets the change reason in the field ``_change_reason`` of the instance. Also, is possible to pass
the ``_change_reason`` explicitly. For this, after a save or delete in an instance, is necessary call the
function ``utils.update_change_reason``. The first argument of this function is the instance and the second
is the message that represents the change reason.

For instance, for the model:

.. code-block:: python

    from django.db import models
    from simple_history.models import HistoricalRecords

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        history = HistoricalRecords()

You can create an instance with an implicit change reason.

.. code-block:: python

    poll = Poll(question='Question 1')
    poll._change_reason = 'Add a question'
    poll.save()

Or you can pass the change reason explicitly:

.. code-block:: python

    from simple_history.utils import update_change_reason

    poll = Poll(question='Question 1')
    poll.save()
    update_change_reason(poll, 'Add a question')


Deleting historical record
--------------------------

In some circumstances you may want to delete all the historical records when the master record is deleted.  This can
be accomplished by setting ``cascade_delete_history=True``.

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        history = HistoricalRecords(cascade_delete_history=True)



Allow tracking to be inherited
---------------------------------

By default history tracking is only added for the model that is passed
to ``register()`` or has the ``HistoricalRecords`` descriptor. By
passing ``inherit=True`` to either way of registering you can change
that behavior so that any child model inheriting from it will have
historical tracking as well. Be careful though, in cases where a model
can be tracked more than once, ``MultipleRegistrationsError`` will be
raised.

.. code-block:: python

    from django.contrib.auth.models import User
    from django.db import models
    from simple_history import register
    from simple_history.models import HistoricalRecords

    # register() example
    register(User, inherit=True)

    # HistoricalRecords example
    class Poll(models.Model):
        history = HistoricalRecords(inherit=True)

Both ``User`` and ``Poll`` in the example above will cause any model
inheriting from them to have historical tracking as well.

History Model In Different App
------------------------------

By default the app_label for the history model is the same as the base model.
In some circumstances you may want to have the history models belong in a different app.
This will support creating history models in a different database to the base model using
database routing functionality based on app_label.
To configure history models in a different app, add this to the HistoricalRecords instantiation
or the record invocation: ``app="SomeAppName"``.

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        history = HistoricalRecords(app="SomeAppName")

    class Opinion(models.Model):
        opinion = models.CharField(max_length=2000)

    register(Opinion, app="SomeAppName")


`FileField` as a `CharField`
----------------------------

By default a ``FileField`` in the base model becomes a ``TextField`` in the history model.
This is a historical choice that django-simple-history preserves for backwards
compatibility; it is more correct for a ``FileField`` to be converted to a
``CharField`` instead. To opt into the new behavior, set the following line in your
``settings.py`` file:

.. code-block:: python

    SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD = True

