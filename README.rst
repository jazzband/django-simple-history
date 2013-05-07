django-simple-history
=====================

.. image:: https://secure.travis-ci.org/treyhunner/django-simple-history.png?branch=master
   :target: http://travis-ci.org/treyhunner/django-simple-history
.. image:: https://coveralls.io/repos/treyhunner/django-simple-history/badge.png?branch=master
   :target: https://coveralls.io/r/treyhunner/django-simple-history

django-simple-history is a tool to store state of DB objects on every create/update/delete.

Install
-------

This package is available on `PyPI`_ and `Crate.io`_.

Install from PyPI with ``pip``:

.. code-block:: bash

    $ pip install django-simple-history

.. _pypi: https://pypi.python.org/pypi/django-simple-history/
.. _crate.io: https://crate.io/packages/django-simple-history/

Basic usage
-----------
Using this package is _really_ simple; you just have to import HistoricalRecords and create an instance of it on every model you want to historically track.

On your models you need to include the following line at the top:

.. code-block:: python

    from simple_history.models import HistoricalRecords

Then in your model class, include the following line:

.. code-block:: python

    history = HistoricalRecords()

Then from either the model class or from an instance, you can access history.all() which will give you either every history item of the class, or every history item of the specific instance.

Example
-------
Models:

.. code-block:: python

    class Poll(models.Model):
        question = models.CharField(max_length = 200)
        pub_date = models.DateTimeField('date published')

        history = HistoricalRecords()

    class Choice(models.Model):
        poll = models.ForeignKey(Poll)
        choice = models.CharField(max_length=200)
        votes = models.IntegerField()

        history = HistoricalRecords()

Usage:

.. code-block:: pycon

    >>> from poll.models import Poll, Choice
    >>> Poll.objects.all()
    []
    >>> import datetime
    >>> p = Poll(question="what's up?", pub_date=datetime.datetime.now())
    >>> p.save()
    >>> p
    <Poll: Poll object>
    >>> p.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]
    >>> p.pub_date = datetime.datetime(2007,4,1,0,0)
    >>> p.save()
    >>> p.history.all()
    [<HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>, <HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]
    >>> p.choice_set.create(choice='Not Much', votes=0)
    <Choice: Choice object>
    >>> p.choice_set.create(choice='The sky', votes=0)
    <Choice: Choice object>
    >>> c = p.choice_set.create(choice='Just hacking again', votes=0)
    >>> c.poll
    <Poll: Poll object>
    >>> c.history.all()
    [<HistoricalChoice: Choice object as of 2010-10-25 18:05:30.160595>]
    >>> Choice.history
    <simple_history.manager.HistoryManager object at 0x1cc4290>
    >>> Choice.history.all()
    [<HistoricalChoice: Choice object as of 2010-10-25 18:05:30.160595>, <HistoricalChoice: Choice object as of 2010-10-25 18:05:12.183340>, <HistoricalChoice: Choice object as of 2010-10-25 18:04:59.047351>]


Admin views
-----------
Inheriting your admin model from SimpleHistoryAdmin will introduce a history button on the object details page, and let you have access to the full history of an object.

Example
-------
Admin:

.. code-block:: python

    from django.contrib import admin
    from simple_history.admin import SimpleHistoryAdmin
    from .models import Poll, Choice

    admin.site.register(Poll, SimpleHistoryAdmin)
    admin.site.register(Choice, SimpleHistoryAdmin)
