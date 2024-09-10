Disable Creating Historical Records
===================================

``save_without_historical_record()`` and ``delete_without_historical_record()``
-------------------------------------------------------------------------------

These methods are automatically added to a model when registering it for history-tracking
(i.e. defining a ``HistoricalRecords``  manager on the model),
and can be called instead of ``save()`` and ``delete()``, respectively.

Using the ``disable_history()`` context manager
-----------------------------------------------

``disable_history()`` has three ways of being called:

#. With no arguments: This will disable all historical record creation
   (as if the ``SIMPLE_HISTORY_ENABLED`` setting was set to ``False``; see below)
   within the context manager's ``with`` block.
#. With ``only_for_model``: Only disable history creation for the provided model type.
#. With ``instance_predicate``: Only disable history creation for model instances passing
   this predicate.

See some examples below:

.. code-block:: python

    from simple_history.utils import disable_history

    # No historical records are created
    with disable_history():
        User.objects.create(...)
        Poll.objects.create(...)

    # A historical record is only created for the poll
    with disable_history(only_for_model=User):
        User.objects.create(...)
        Poll.objects.create(...)

    # A historical record is created for the second poll, but not for the first poll
    # (remember to check the instance type in the passed function if you expect
    # historical records of more than one model to be created inside the `with` block)
    with disable_history(instance_predicate=lambda poll: "ignore" in poll.question):
        Poll.objects.create(question="ignore this")
        Poll.objects.create(question="what's up?")

Overriding ``create_historical_record()``
-----------------------------------------

For even more fine-grained control, you can subclass ``HistoricalRecords`` and override
its ``create_historical_record()`` method, for example like this:

.. code-block:: python

    class CustomHistoricalRecords(HistoricalRecords):
        def create_historical_record(
            self, instance: models.Model, history_type: str, *args, **kwargs
        ) -> None:
        # Don't create records for "ignore" polls that are being deleted
        if "ignore" in poll.question and history_type == "-":
            return

        super().create_historical_record(instance, history_type, *args, **kwargs)


    class Poll(models.Model):
        # ...
        history = CustomHistoricalRecords()

The ``SIMPLE_HISTORY_ENABLED`` setting
--------------------------------------

Disable the creation of historical records for *all* models
by adding the following line to your settings:

.. code-block:: python

    SIMPLE_HISTORY_ENABLED = False
