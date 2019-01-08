History Diffing
===============

When you have two instances of the same ``HistoricalRecord`` (such as the ``HistoricalPoll`` example above),
you can perform diffs to see what changed. This will result in a ``ModelDelta`` containing the following properties:

1. A list with each field changed between the two historical records
2. A list with the names of all fields that incurred changes from one record to the other
3. the old and new records.

This may be useful when you want to construct timelines and need to get only the model modifications.

.. code-block:: python

    p = Poll.objects.create(question="what's up?")
    p.question = "what's up, man?"
    p.save()

    new_record, old_record = p.history.all()
    delta = new_record.diff_against(old_record)
    for change in delta.changes:
        print("{} changed from {} to {}".format(change.field, change.old, change.new))
