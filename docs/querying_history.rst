Querying History
================

Querying history on a model instance
------------------------------------

The ``HistoricalRecords`` object on a model instance can be used in the same
way as a model manager:

.. code-block:: pycon

    >>> from polls.models import Poll, Choice
    >>> from datetime import datetime
    >>> poll = Poll.objects.create(question="what's up?", pub_date=datetime.now())
    >>>
    >>> poll.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

Whenever a model instance is saved a new historical record is created:

.. code-block:: pycon

    >>> poll.pub_date = datetime(2007, 4, 1, 0, 0)
    >>> poll.save()
    >>> poll.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>, <HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

Querying history on a model class
---------------------------------

Historical records for all instances of a model can be queried by using the
``HistoricalRecords`` manager on the model class.  For example historical
records for all ``Choice`` instances can be queried by using the manager on the
``Choice`` model class:

.. code-block:: pycon

    >>> choice1 = poll.choice_set.create(choice_text='Not Much', votes=0)
    >>> choice2 = poll.choice_set.create(choice_text='The sky', votes=0)
    >>>
    >>> Choice.history
    <simple_history.manager.HistoryManager object at 0x1cc4290>
    >>> Choice.history.all()
    [<HistoricalChoice: Choice object as of 2010-10-25 18:05:12.183340>, <HistoricalChoice: Choice object as of 2010-10-25 18:04:59.047351>]

Because the history is model, you can also filter it like regularly QuerySets,
e.g. ``Choice.history.filter(choice_text='Not Much')`` will work!

Getting previous and next historical record
-------------------------------------------

If you have a historical record for an instance and would like to retrieve the previous historical record (older) or next historical record (newer), `prev_record` and `next_record` read-only attributes can be used, respectively.

.. code-block:: pycon

    >>> from polls.models import Poll, Choice
    >>> from datetime import datetime
    >>> poll = Poll.objects.create(question="what's up?", pub_date=datetime.now())
    >>>
    >>> record = poll.history.first()
    >>> record.prev_record
    None
    >>> record.next_record
    None
    >>> poll.question = "what is up?"
    >>> poll.save()
    >>> record.next_record
    <HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>

If a historical record is the first record, `prev_record` will be `None`.  Similarly, if it is the latest record, `next_record` will be `None`

Reverting the Model
-------------------

``SimpleHistoryAdmin`` allows users to revert back to an old version of the
model through the admin interface. You can also do this programmatically. To
do so, you can take any historical object, and save the associated instance.
For example, if we want to access the earliest ``HistoricalPoll``, for an
instance of ``Poll``, we can do:

.. code-block:: pycon

    >>> poll.history.earliest()
    <HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>

And to revert to that ``HistoricalPoll`` instance, we can do:

.. code-block:: pycon

    >>> earliest_poll = poll.history.earliest()
    >>> earliest_poll.instance.save()

This will change the ``poll`` instance to have the data from the
``HistoricalPoll`` object and it will create a new row in the
``HistoricalPoll`` table indicating that a new change has been made.


as_of
-----

This method will return an instance of the model as it would have existed at
the provided date and time.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> poll.history.as_of(datetime(2010, 10, 25, 18, 4, 0))
    <Poll: Poll object as of 2010-10-25 18:03:29.855689>
    >>> poll.history.as_of(datetime(2010, 10, 25, 18, 5, 0))
    <Poll: Poll object as of 2010-10-25 18:04:13.814128>

most_recent
-----------

This method will return the most recent copy of the model available in the
model history.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> poll.history.most_recent()
    <Poll: Poll object as of 2010-10-25 18:04:13.814128>


Save without a historical record
--------------------------------

If you want to save a model without a historical record, you can use the following:

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        history = HistoricalRecords()

        def save_without_historical_record(self, *args, **kwargs):
            self.skip_history_when_saving = True
            try:
                ret = self.save(*args, **kwargs)
            finally:
                del self.skip_history_when_saving
            return ret


    poll = Poll(question='something')
    poll.save_without_historical_record()


Filtering data using a relationship to the model
------------------------------------------------

To filter changes to the data, a relationship to the history can be established. For example, all data records in which a particular user was involved.

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        log = HistoricalRecords(related_name='history')


    Poll.objects.filter(history__history_user=4)

You can also prefetch the objects with this relationship using somthing like this for example to prefetch order by history_date descending:

.. code-block:: python

    Poll.objects.filter(something).prefetch_related(Prefetch('history', queryset=Poll.history.order_by('-history_date'),
                                                to_attr='ordered_histories')
