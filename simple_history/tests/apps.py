from django.apps import AppConfig
from simple_history.signals import pre_create_historical_record


def add_history_ip_address(sender, **kwargs):
    history_instance = kwargs['history_instance']
    history_instance.ip_address = '127.0.0.1'


class TestsConfig(AppConfig):
    name = 'simple_history.tests'
    verbose_name = 'Tests'

    def ready(self):
        from simple_history.tests.models \
            import HistoricalPollWithHistoricalIPAddress

        pre_create_historical_record.connect(
            add_history_ip_address,
            sender=HistoricalPollWithHistoricalIPAddress
        )
