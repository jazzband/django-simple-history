from django.apps import AppConfig


class SimpleHistoryConfig(AppConfig):
    name = 'simple_history'
    verbose_name = "Simple history"
    models_to_finalize = []

    def ready(self, *args, **kwargs):
        for records, cls in self.models_to_finalize:
            records.finalize(cls)
        return super(SimpleHistoryConfig, self).ready(*args, **kwargs)
