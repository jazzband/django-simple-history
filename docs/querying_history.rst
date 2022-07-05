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

The HistoryManager allows you to query a point in time for the latest historical
records or instances.  When called on an instance's history manager, the ``as_of``
method will return the instance from the specified point in time, if the instance
existed at that time, or raise DoesNotExist.  When called on a model's history
manager, the ``as_of`` method will return instances from a specific date and time
that you specify, returning a queryset that you can use to further filter the result.

.. code-block:: pycon

    >>> t0 = datetime.now()
    >>> document1 = RankedDocument.objects.create(rank=42)
    >>> document2 = RankedDocument.objects.create(rank=84)
    >>> t1 = datetime.now()

    >>> RankedDocument.history.as_of(t1)
    <HistoricalQuerySet [
        <RankedDocument: RankedDocument object (1)>,
        <RankedDocument: RankedDocument object (2)>
    ]>

    >>> RankedDocument.history.as_of(t1).filter(rank__lte=50)
    <HistoricalQuerySet [
        <RankedDocument: RankedDocument object (1)>
    ]>

``as_of`` is a convenience: the following two queries are identical.

.. code-block:: pycon

    RankedDocument.history.as_of(t1)
    RankedDocument.history.filter(history_date__lte=t1).latest_of_each().as_instances()

If you filter by `pk` the behavior depends on whether the queryset is
returning instances or historical records.  When the queryset is returning
instances, `pk` is mapped to the original model's primary key field.
When the queryset is returning historical records, `pk` refers to the
`history_id` primary key.


is_historic and to_historic
---------------------------

If you use `as_of` to query history, the resulting instance will have an
attribute named `_history` added to it.  This property will contain the
historical model record that the instance was derived from.  Calling
is_historic is an easy way to check if an instance was derived from a
historic point in time (even if it is the most recent version).

You can use `to_historic` to return the historical model that was used
to furnish the instance at hand, if it is actually historic.


HistoricForeignKey
------------------

If you have two historic tables linked by foreign key, you can change it
to use a HistoricForeignKey so that chasing relations from an `as_of`
acquired instance (at a specific point in time) will honor that point in time
when accessing the related object(s).  This works for both forward and
reverse relationships.

See the `HistoricForeignKeyTest` code and models for an example.


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

Or disable history records for all models by putting following lines in your ``settings.py`` file:

.. code-block:: python

    SIMPLE_HISTORY_ENABLED = False


Filtering data using a relationship to the model
------------------------------------------------

To filter changes to the data, a relationship to the history can be established. For example, all data records in which a particular user was involved.

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length=200)
        log = HistoricalRecords(related_name='history')


    Poll.objects.filter(history__history_user=4)

You can also prefetch the objects with this relationship using something like this for example to prefetch order by history_date descending:

.. code-block:: python

    Poll.objects.filter(something).prefetch_related(Prefetch('history', queryset=Poll.history.order_by('-history_date'),
                                                to_attr='ordered_histories')
