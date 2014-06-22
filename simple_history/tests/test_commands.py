from datetime import datetime
from django.test import TestCase
from django.core import management

from . import models


class TestPopulateHistory(TestCase):
    command_name = 'populate_history'

    def test_auto_populate(self):
        models.Poll.objects.create(question="Will this populate?", pub_date=datetime.now())
        models.Poll.history.all().delete()
        management.call_command(self.command_name, auto="")
        self.assertEqual(models.Poll.history.all().count(), 1)
