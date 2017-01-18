from django.db import models
from simple_history.models import HistoricalRecords


class DoYouKnow(models.Model):
    pass


class WhatIMean(DoYouKnow):
    pass


class Yar(models.Model):
    what = models.ForeignKey(WhatIMean)
    history = HistoricalRecords()
