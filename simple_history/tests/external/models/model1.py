from __future__ import unicode_literals

from django.db import models
from simple_history.models import HistoricalRecords


class AbstractExternal(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
        app_label = "external"


class AbstractExternal2(models.Model):
    history = HistoricalRecords(
        inherit=True, custom_model_name=lambda x: "Audit{}".format(x)
    )

    class Meta:
        abstract = True
        app_label = "external"


class AbstractExternal3(models.Model):
    history = HistoricalRecords(
        inherit=True, app="external", custom_model_name=lambda x: "Audit{}".format(x)
    )

    class Meta:
        abstract = True
        app_label = "external"
