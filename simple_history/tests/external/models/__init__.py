from __future__ import unicode_literals

from django.db import models
from simple_history.models import HistoricalRecords

from .model2 import ExternalModel2
from .model4 import ExternalModel4


class Poll(models.Model):
    """Test model for same-named historical models

    This model intentionally conflicts with the 'Polls' model in 'tests.models'.
    """
    history = HistoricalRecords(user_related_name='+')

    class Meta:
        app_label = 'external'
