Disable Creating Historical Records
===================================

Save without creating historical records
----------------------------------------

If you want to save model objects without triggering the creation of any historical
records, you can do the following:

.. code-block:: python

    poll.skip_history_when_saving = True
    poll.save()
    # We recommend deleting the attribute afterward
    del poll.skip_history_when_saving

This also works when creating an object, but only when calling ``save()``:

.. code-block:: python

    # Note that `Poll.objects.create()` is not called
    poll = Poll(question="Why?")
    poll.skip_history_when_saving = True
    poll.save()
    del poll.skip_history_when_saving

.. note::
    Historical records will always be created when calling the ``create()`` manager method.

Alternatively, call the ``save_without_historical_record()`` method on each object
instead of ``save()``.
This method is automatically added to a model when registering it for history-tracking
(i.e. defining a ``HistoricalRecords``  manager field on the model),
and it looks like this:

.. code-block:: python

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

Or disable the creation of historical records for *all* models
by adding the following line to your settings:

.. code-block:: python

    SIMPLE_HISTORY_ENABLED = False
