from __future__ import unicode_literals

from django.db import models
from simple_history.models import HistoricalRecords


class ExternalModel2(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        app_label = 'external'
