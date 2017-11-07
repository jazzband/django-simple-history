from __future__ import unicode_literals

from django.db import models
from simple_history.models import HistoricalRecords


class AbstractExternal(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
        app_label = 'external'
