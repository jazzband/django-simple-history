from django.db import models

from simple_history import register
from simple_history.models import HistoricalRecords
from simple_history.tests.custom_user.models import CustomUser


class AbstractExternal(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


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


class ExternalModel(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()


class ExternalModelRegistered(models.Model):
    name = models.CharField(max_length=100)


register(ExternalModelRegistered, app="simple_history.tests", manager_name="histories")


class ExternalModelWithCustomUserIdField(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords(history_user_id_field=models.IntegerField(null=True))


class Poll(models.Model):
    """Test model for same-named historical models

    This model intentionally conflicts with the 'Polls' model in 'tests.models'.
    """

    history = HistoricalRecords(user_related_name="+")
