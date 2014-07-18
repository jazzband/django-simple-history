from django.apps import AppConfig


models_to_finalize = []


class SimpleHistoryConfig(AppConfig):
    name = 'simple_history'
    verbose_name = "Simple history"

    def ready(self, *args, **kwargs):
        for records, cls in models_to_finalize:
            records.finalize(cls)
        return super(SimpleHistoryConfig, self).ready(*args, **kwargs)
