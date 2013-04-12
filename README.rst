django-simple-history is a tool to store state of DB objects on every create/update/delete. It has been tested to work in django 1.X (including 1.2.3 as of 10/25/2010).

== Install ==
Download the tar.gz, extract it and run the following inside the directory:
    python setup.py install

== Basic usage ==
Using this package is _really_ simple; you just have to import HistoricalRecords and create an instance of it on every model you want to historically track.

On your models you need to include the following line at the top:
    from simple_history.models import HistoricalRecords

Then in your model class, include the following line:
    history = HistoricalRecords()

Then from either the model class or from an instance, you can access history.all() which will give you either every history item of the class, or every history item of the specific instance.

== Example ==
class Poll(models.Model):
    question = models.CharField(max_length = 200)
    pub_date = models.DateTimeField('date published')

    history = HistoricalRecords()

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    history = HistoricalRecords()
                                        

$ ./manage.py shell
In [2]: from poll.models import Poll, Choice

In [3]: Poll.objects.all()
Out[3]: []

In [4]: import datetime

In [5]: p = Poll(question="what's up?", pub_date=datetime.datetime.now())

In [6]: p.save()

In [7]: p
Out[7]: <Poll: Poll object>

In [9]: p.history.all()
Out[9]: [<HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

In [10]: p.pub_date = datetime.datetime(2007,4,1,0,0)

In [11]: p.save()

In [13]: p.history.all()
Out[13]: [<HistoricalPoll: Poll object as of 2010-10-25 18:04:13.814128>, <HistoricalPoll: Poll object as of 2010-10-25 18:03:29.855689>]

In [14]: p.choice_set.create(choice='Not Much', votes=0)
Out[14]: <Choice: Choice object>

In [15]: p.choice_set.create(choice='The sky', votes=0)
Out[15]: <Choice: Choice object>

In [16]: c = p.choice_set.create(choice='Just hacking again', votes=0)

In [17]: c.poll
Out[17]: <Poll: Poll object>

In [19]: c.history.all()
Out[19]: [<HistoricalChoice: Choice object as of 2010-10-25 18:05:30.160595>]

In [20]: Choice.history
Out[20]: <simple_history.manager.HistoryManager object at 0x1cc4290>

In [21]: Choice.history.all()
Out[21]: [<HistoricalChoice: Choice object as of 2010-10-25 18:05:30.160595>, <HistoricalChoice: Choice object as of 2010-10-25 18:05:12.183340>, <HistoricalChoice: Choice object as of 2010-10-25 18:04:59.047351>]

