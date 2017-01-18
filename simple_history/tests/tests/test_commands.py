from contextlib import contextmanager
from datetime import datetime

from six.moves import cStringIO as StringIO
from django.test import TestCase
from django.core import management

from simple_history import models as sh_models
from simple_history.management.commands import populate_history

from .. import models


@contextmanager
def replace_registry(new_value=None):
    hidden_registry = sh_models.registered_models
    sh_models.registered_models = new_value or {}
    try:
        yield
    except Exception:
        raise
    finally:
        sh_models.registered_models = hidden_registry


class TestPopulateHistory(TestCase):
    command_name = 'populate_history'
    command_error = (management.CommandError, SystemExit)

    def test_no_args(self):
        out = StringIO()
        management.call_command(self.command_name,
                                stdout=out, stderr=StringIO())
        self.assertIn(populate_history.Command.COMMAND_HINT, out.getvalue())

    def test_bad_args(self):
        test_data = (
            (populate_history.Command.MODEL_NOT_HISTORICAL, ("tests.place",)),
            (populate_history.Command.MODEL_NOT_FOUND, ("invalid.model",)),
            (populate_history.Command.MODEL_NOT_FOUND, ("bad_key",)),
        )
        for msg, args in test_data:
            out = StringIO()
            self.assertRaises(self.command_error, management.call_command,
                              self.command_name, *args,
                              stdout=StringIO(), stderr=out)
            self.assertIn(msg, out.getvalue())

    def test_auto_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        management.call_command(self.command_name, auto=True,
                                stdout=StringIO(), stderr=StringIO())
        self.assertEqual(models.Poll.history.all().count(), 1)

    def test_specific_populate(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        models.Book.objects.create(isbn="9780007117116")
        models.Book.history.all().delete()
        management.call_command(self.command_name, "tests.book",
                                stdout=StringIO(), stderr=StringIO())
        self.assertEqual(models.Book.history.all().count(), 1)
        self.assertEqual(models.Poll.history.all().count(), 0)

    def test_failing_wont_save(self):
        models.Poll.objects.create(question="Will this populate?",
                                   pub_date=datetime.now())
        models.Poll.history.all().delete()
        self.assertRaises(self.command_error,
                          management.call_command, self.command_name,
                          "tests.poll", "tests.invalid_model",
                          stdout=StringIO(), stderr=StringIO())
        self.assertEqual(models.Poll.history.all().count(), 0)

    def test_multi_table(self):
        data = {'rating': 5, 'name': "Tea 'N More"}
        models.Restaurant.objects.create(**data)
        models.Restaurant.updates.all().delete()
        management.call_command(self.command_name, 'tests.restaurant',
                                stdout=StringIO(), stderr=StringIO())
        update_record = models.Restaurant.updates.all()[0]
        for attr, value in data.items():
            self.assertEqual(getattr(update_record, attr), value)

    def test_existing_objects(self):
        data = {'rating': 5, 'name': "Tea 'N More"}
        out = StringIO()
        models.Restaurant.objects.create(**data)
        pre_call_count = models.Restaurant.updates.count()
        management.call_command(self.command_name, 'tests.restaurant',
                                stdout=StringIO(), stderr=out)
        self.assertEqual(models.Restaurant.updates.count(), pre_call_count)
        self.assertIn(populate_history.Command.EXISTING_HISTORY_FOUND,
                      out.getvalue())

    def test_no_historical(self):
        out = StringIO()
        with replace_registry():
            management.call_command(self.command_name, auto=True,
                                    stdout=out)
        self.assertIn(populate_history.Command.NO_REGISTERED_MODELS,
                      out.getvalue())
