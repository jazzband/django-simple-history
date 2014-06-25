from six.moves import cStringIO as StringIO
from datetime import datetime
from django.test import TestCase
from django.core import management
from simple_history.management.commands import populate_history

from .. import models


class TestPopulateHistory(TestCase):
    command_name = 'populate_history'

    def test_no_args(self):
        out = StringIO()
        management.call_command(self.command_name, stdout=out)
        self.assertIn(populate_history.Command.COMMAND_HINT, out.getvalue())

    def test_bad_args(self):
        for args in (("tests.place",), ("invalid.model",)):
            self.assertRaises(management.CommandError, management.call_command,
                              self.command_name, *args, stderr=StringIO())

    def test_auto_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        management.call_command(self.command_name, auto=True,
                                stdout=StringIO())
        self.assertEqual(models.Poll.history.all().count(), 1)

    def test_specific_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        models.Book.objects.create(isbn="9780007117116")
        models.Book.history.all().delete()
        management.call_command(self.command_name, "tests.book",
                                stdout=StringIO())
        self.assertEqual(models.Book.history.all().count(), 1)
        self.assertEqual(models.Poll.history.all().count(), 0)

    def test_failing_wont_save(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        self.assertRaises(management.CommandError, management.call_command,
                          self.command_name, "tests.poll",
                          "tests.invalid_model", stderr=StringIO())
        self.assertEqual(models.Poll.history.all().count(), 0)

    def test_multi_table(self):
        data = {'rating': 5, 'name': "Tea 'N More"}
        models.Restaurant(**data).save_without_historical_record()
        management.call_command(self.command_name, 'tests.restaurant',
                                stdout=StringIO())
        update_record = models.Restaurant.updates.all()[0]
        for attr, value in data.items():
            self.assertEqual(getattr(update_record, attr), value)
