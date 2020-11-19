from django.db import models

from simple_history.models import HistoricalRecords


class DoYouKnow(models.Model):
    pass


class WhatIMean(DoYouKnow):
    pass


class Yar(models.Model):
    what = models.ForeignKey(WhatIMean, on_delete=models.CASCADE)
    history = HistoricalRecords()


class CustomAttrNameForeignKey(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        self.attr_name = kwargs.pop("attr_name", None)
        super(CustomAttrNameForeignKey, self).__init__(*args, **kwargs)

    def get_attname(self):
        return self.attr_name or super(CustomAttrNameForeignKey, self).get_attname()

    def deconstruct(self):
        name, path, args, kwargs = super(CustomAttrNameForeignKey, self).deconstruct()
        if self.attr_name:
            kwargs["attr_name"] = self.attr_name
        return name, path, args, kwargs


class ModelWithCustomAttrForeignKey(models.Model):
    what_i_mean = CustomAttrNameForeignKey(
        WhatIMean, models.CASCADE, attr_name="custom_attr_name"
    )
    history = HistoricalRecords()
