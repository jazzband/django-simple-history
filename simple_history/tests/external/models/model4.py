from __future__ import unicode_literals

from django.db import models
from simple_history import register


class ExternalModel4(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'external'

register(ExternalModel4, app='simple_history.tests',
         manager_name='histories')
