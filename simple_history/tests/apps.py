from django.apps import AppConfig
from simple_history.models import HistoricalRecords
from simple_history.signals import pre_create_historical_record


class TestsConfig(AppConfig):
    name = 'simple_history.tests'
    verbose_name = 'Tests'

    def ready(self):
        from simple_history.tests.models \
            import HistoricalPollWithHistoricalIPAddress
        from simple_history.tests.tests.utils import add_history_ip_address

        pre_create_historical_record.connect(
            add_history_ip_address,
            sender=HistoricalPollWithHistoricalIPAddress,
            dispatch_uid='add_history_ip_address'
        )
