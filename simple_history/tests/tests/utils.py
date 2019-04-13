import django
from django.conf import settings

request_middleware = "simple_history.middleware.HistoryRequestMiddleware"

WHITELIST = (
    'historicalmodelwithhistoryindifferentdb',
)

if django.__version__ >= "2.0":
    middleware_override_settings = {
        "MIDDLEWARE": (settings.MIDDLEWARE + [request_middleware])
    }
else:
    middleware_override_settings = {
        "MIDDLEWARE_CLASSES": (settings.MIDDLEWARE_CLASSES + [request_middleware])
    }


class TestDbRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "external":
            return "other"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "external":
            return "other"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == "external" and obj2._meta.app_label == "external":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        print(db, model_name)
        if app_label == "external" or model_name in WHITELIST:
            return db == "other"
        elif db == "other":
            return False
        else:
            return None


database_router_override_settings = {
    "DATABASE_ROUTERS": ["simple_history.tests.tests.utils.TestDbRouter"]
}
