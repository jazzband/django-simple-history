import django
from django.conf import settings

simple_history_middleware = 'simple_history.middleware.HistoryRequestMiddleware'

if django.__version__ >= '2.0':
    middleware_override_settings = {
        'MIDDLEWARE': (
            settings.MIDDLEWARE + [simple_history_middleware]
        )
    }
else:
    middleware_override_settings = {
        'MIDDLEWARE_CLASSES': (
            settings.MIDDLEWARE_CLASSES + [simple_history_middleware]
        )
    }
