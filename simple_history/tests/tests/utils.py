import django
from django.conf import settings

from simple_history.tests.models import HistoricalModelWithHistoryInDifferentDb

request_middleware = "simple_history.middleware.HistoryRequestMiddleware"

OTHER_DB_NAME = "other"

middleware_override_settings = {
    "MIDDLEWARE": (settings.MIDDLEWARE + [request_middleware])
}


class TestDbRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "external":
            return OTHER_DB_NAME
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "external":
            return OTHER_DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == "external" and obj2._meta.app_label == "external":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "external":
            return db == OTHER_DB_NAME
        elif db == OTHER_DB_NAME:
            return False
        else:
            return None


database_router_override_settings = {
    "DATABASE_ROUTERS": ["simple_history.tests.tests.utils.TestDbRouter"]
}


class TestModelWithHistoryInDifferentDbRouter(object):
    def db_for_read(self, model, **hints):
        if model == HistoricalModelWithHistoryInDifferentDb:
            return OTHER_DB_NAME
        return None

    def db_for_write(self, model, **hints):
        if model == HistoricalModelWithHistoryInDifferentDb:
            return OTHER_DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if isinstance(obj1, HistoricalModelWithHistoryInDifferentDb) or isinstance(
            obj2, HistoricalModelWithHistoryInDifferentDb
        ):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == HistoricalModelWithHistoryInDifferentDb._meta.model_name:
            return db == OTHER_DB_NAME
        return None


database_router_override_settings_history_in_diff_db = {
    "DATABASE_ROUTERS": [
        "simple_history.tests.tests.utils.TestModelWithHistoryInDifferentDbRouter"
    ]
}
