import django
from django.conf import settings

request_middleware = 'simple_history.middleware.HistoryRequestMiddleware'

if django.__version__ >= '2.0':
    middleware_override_settings = {
        'MIDDLEWARE': (
            settings.MIDDLEWARE + [request_middleware]
        )
    }
else:
    middleware_override_settings = {
        'MIDDLEWARE_CLASSES': (
            settings.MIDDLEWARE_CLASSES + [request_middleware]
        )
    }


def add_history_ip_address(sender, **kwargs):
    history_instance = kwargs['history_instance']
    if history_instance.question == 'read IP from request':
        from simple_history.models import HistoricalRecords
        history_instance.ip_address = \
            HistoricalRecords.thread.request.META['REMOTE_ADDR']
    else:
        history_instance.ip_address = '192.168.0.1'
