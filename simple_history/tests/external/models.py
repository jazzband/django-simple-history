
from django.db import models
from simple_history.models import HistoricalRecords
from simple_history import register

class ExternalModel2(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

class ExternalModel4(models.Model):
    name = models.CharField(max_length=100)

register(ExternalModel4, app='simple_history.tests',
    manager_name='histories')
