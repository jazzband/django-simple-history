Disable Creating Historical Records
===================================

``save_without_historical_record()`` and ``delete_without_historical_record()``
-------------------------------------------------------------------------------

These methods are automatically added to a model when registering it for history-tracking
(i.e. defining a ``HistoricalRecords``  manager on the model),
and can be called instead of ``save()`` and ``delete()``, respectively.

Setting the ``skip_history_when_saving`` attribute
--------------------------------------------------

If you want to save or delete model objects without triggering the creation of any
historical records, you can do the following:

.. code-block:: python

    poll.skip_history_when_saving = True
    # It applies both when saving...
    poll.save()
    # ...and when deleting
    poll.delete()
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

The ``SIMPLE_HISTORY_ENABLED`` setting
--------------------------------------

Disable the creation of historical records for *all* models
by adding the following line to your settings:

.. code-block:: python

    SIMPLE_HISTORY_ENABLED = False
