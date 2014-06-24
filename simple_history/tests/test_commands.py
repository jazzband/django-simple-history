from six.moves import cStringIO as StringIO
from datetime import datetime
from django.test import TestCase
from django.core import management

from . import models


class TestPopulateHistory(TestCase):
    command_name = 'populate_history'

    def test_auto_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        management.call_command(self.command_name, auto=True, stdout=StringIO())
        self.assertEqual(models.Poll.history.all().count(), 1)

    def test_specific_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        models.Book.objects.create(isbn="9780007117116")
        models.Book.history.all().delete()
        management.call_command(self.command_name, "tests.book", stdout=StringIO())
        self.assertEqual(models.Book.history.all().count(), 1)
        self.assertEqual(models.Poll.history.all().count(), 0)
