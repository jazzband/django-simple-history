from enum import Enum
from typing import Type

from django.conf import settings
from django.db.models import Model
from django.test import TestCase

request_middleware = "simple_history.middleware.HistoryRequestMiddleware"

OTHER_DB_NAME = "other"

middleware_override_settings = {
    "MIDDLEWARE": (settings.MIDDLEWARE + [request_middleware])
}


class HistoricalTestCase(TestCase):
    def assertRecordValues(self, record, klass: Type[Model], values_dict: dict):
        """
        Fail if ``record`` doesn't contain the field values in ``values_dict``.
        ``record.history_object`` is also checked.
        History-tracked fields in ``record`` that are not in ``values_dict``, are not
        checked.

        :param record: A historical record.
        :param klass: The type of the history-tracked class of ``record``.
        :param values_dict: Field names of ``record`` mapped to their expected values.
        """
        for key, value in values_dict.items():
            self.assertEqual(getattr(record, key), value)

        self.assertEqual(record.history_object.__class__, klass)
        for key, value in values_dict.items():
            if key not in ("history_type", "history_change_reason"):
                self.assertEqual(getattr(record.history_object, key), value)


class TestDbRouter:
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


class TestModelWithHistoryInDifferentDbRouter:
    def db_for_read(self, model, **hints):
        # Avoids circular importing
        from ..models import HistoricalModelWithHistoryInDifferentDb

        if model == HistoricalModelWithHistoryInDifferentDb:
            return OTHER_DB_NAME
        return None

    def db_for_write(self, model, **hints):
        # Avoids circular importing
        from ..models import HistoricalModelWithHistoryInDifferentDb

        if model == HistoricalModelWithHistoryInDifferentDb:
            return OTHER_DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Avoids circular importing
        from ..models import HistoricalModelWithHistoryInDifferentDb

        if isinstance(obj1, HistoricalModelWithHistoryInDifferentDb) or isinstance(
            obj2, HistoricalModelWithHistoryInDifferentDb
        ):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Avoids circular importing
        from ..models import HistoricalModelWithHistoryInDifferentDb

        if model_name == HistoricalModelWithHistoryInDifferentDb._meta.model_name:
            return db == OTHER_DB_NAME
        return None


database_router_override_settings_history_in_diff_db = {
    "DATABASE_ROUTERS": [
        "simple_history.tests.tests.utils.TestModelWithHistoryInDifferentDbRouter"
    ]
}


class PermissionAction(Enum):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"
    VIEW = "view"
