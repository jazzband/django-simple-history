from django.apps import AppConfig

from . import models


class SimpleHistoryConfig(AppConfig):
    name = 'simple_history'
    verbose_name = "Simple history"
    models_to_finalize = []

    def ready(self):
        for records, cls in models.HistoricalRecords.models_to_finalize:
            records.finalize(cls)
