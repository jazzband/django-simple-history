from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from simple_history import register


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    history = HistoricalRecords()


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

register(Choice)

register(User, app='simple_history.tests', manager_name='histories')
