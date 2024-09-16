from django.conf import settings
from django.db import models
from django.test import TestCase, override_settings

from simple_history.models import HistoricalRecords


@override_settings(SIMPLE_HISTORY_DATE_INDEX="Composite")
class HistoricalIndexTest(TestCase):
    def test_has_composite_index(self):
        self.assertEqual(settings.SIMPLE_HISTORY_DATE_INDEX, "Composite")

        class Foo(models.Model):
            history = HistoricalRecords()

        self.assertEqual(
            ["history_date", "id"], Foo.history.model._meta.indexes[0].fields
        )
