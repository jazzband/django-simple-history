from contextlib import contextmanager
from datetime import datetime, timedelta
from io import StringIO

from django.core import management
from django.test import TestCase

from simple_history import models as sh_models
from simple_history.management.commands import (
    populate_history,
    clean_duplicate_history,
    clean_old_history,
)
from ..models import (
    Book,
    CustomManagerNameModel,
    Place,
    Poll,
    PollWithExcludeFields,
    Restaurant,
)


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
    command_name = "populate_history"
    command_error = (management.CommandError, SystemExit)

    def test_no_args(self):
        out = StringIO()
        management.call_command(self.command_name, stdout=out, stderr=StringIO())
        self.assertIn(populate_history.Command.COMMAND_HINT, out.getvalue())

    def test_bad_args(self):
        test_data = (
            (populate_history.Command.MODEL_NOT_HISTORICAL, ("tests.place",)),
            (populate_history.Command.MODEL_NOT_FOUND, ("invalid.model",)),
            (populate_history.Command.MODEL_NOT_FOUND, ("bad_key",)),
        )
        for msg, args in test_data:
            out = StringIO()
            self.assertRaises(
                self.command_error,
                management.call_command,
                self.command_name,
                *args,
                stdout=StringIO(),
                stderr=out
            )
            self.assertIn(msg, out.getvalue())

    def test_auto_populate(self):
        Poll.objects.create(question="Will this populate?", pub_date=datetime.now())
        Poll.history.all().delete()
        management.call_command(
            self.command_name, auto=True, stdout=StringIO(), stderr=StringIO()
        )
        self.assertEqual(Poll.history.all().count(), 1)

    def test_populate_with_custom_batch_size(self):
        Poll.objects.create(question="Will this populate?", pub_date=datetime.now())
        Poll.history.all().delete()
        management.call_command(
            self.command_name,
            auto=True,
            batchsize=500,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        self.assertEqual(Poll.history.all().count(), 1)

    def test_specific_populate(self):
        Poll.objects.create(question="Will this populate?", pub_date=datetime.now())
        Poll.history.all().delete()
        Book.objects.create(isbn="9780007117116")
        Book.history.all().delete()
        management.call_command(
            self.command_name, "tests.book", stdout=StringIO(), stderr=StringIO()
        )
        self.assertEqual(Book.history.all().count(), 1)
        self.assertEqual(Poll.history.all().count(), 0)

    def test_failing_wont_save(self):
        Poll.objects.create(question="Will this populate?", pub_date=datetime.now())
        Poll.history.all().delete()
        self.assertRaises(
            self.command_error,
            management.call_command,
            self.command_name,
            "tests.poll",
            "tests.invalid_model",
            stdout=StringIO(),
            stderr=StringIO(),
        )
        self.assertEqual(Poll.history.all().count(), 0)

    def test_multi_table(self):
        data = {"rating": 5, "name": "Tea 'N More"}
        Restaurant.objects.create(**data)
        Restaurant.updates.all().delete()
        management.call_command(
            self.command_name, "tests.restaurant", stdout=StringIO(), stderr=StringIO()
        )
        update_record = Restaurant.updates.all()[0]
        for attr, value in data.items():
            self.assertEqual(getattr(update_record, attr), value)

    def test_existing_objects(self):
        data = {"rating": 5, "name": "Tea 'N More"}
        out = StringIO()
        Restaurant.objects.create(**data)
        pre_call_count = Restaurant.updates.count()
        management.call_command(
            self.command_name, "tests.restaurant", stdout=StringIO(), stderr=out
        )
        self.assertEqual(Restaurant.updates.count(), pre_call_count)
        self.assertIn(populate_history.Command.EXISTING_HISTORY_FOUND, out.getvalue())

    def test_no_historical(self):
        out = StringIO()
        with replace_registry({"test_place": Place}):
            management.call_command(self.command_name, auto=True, stdout=out)
        self.assertIn(populate_history.Command.NO_REGISTERED_MODELS, out.getvalue())

    def test_batch_processing_with_batch_size_less_than_total(self):
        data = [
            Poll(id=1, question="Question 1", pub_date=datetime.now()),
            Poll(id=2, question="Question 2", pub_date=datetime.now()),
            Poll(id=3, question="Question 3", pub_date=datetime.now()),
            Poll(id=4, question="Question 4", pub_date=datetime.now()),
        ]
        Poll.objects.bulk_create(data)

        management.call_command(
            self.command_name,
            auto=True,
            batchsize=3,
            stdout=StringIO(),
            stderr=StringIO(),
        )

        self.assertEqual(Poll.history.count(), 4)

    def test_stdout_not_printed_when_verbosity_is_0(self):
        out = StringIO()
        Poll.objects.create(question="Question 1", pub_date=datetime.now())

        management.call_command(
            self.command_name,
            auto=True,
            batchsize=3,
            stdout=out,
            stderr=StringIO(),
            verbosity=0,
        )

        self.assertEqual(out.getvalue(), "")

    def test_stdout_printed_when_verbosity_is_not_specified(self):
        out = StringIO()
        Poll.objects.create(question="Question 1", pub_date=datetime.now())

        management.call_command(
            self.command_name, auto=True, batchsize=3, stdout=out, stderr=StringIO()
        )

        self.assertNotEqual(out.getvalue(), "")

    def test_excluded_fields(self):
        poll = PollWithExcludeFields.objects.create(
            question="Will this work?", pub_date=datetime.now()
        )
        PollWithExcludeFields.history.all().delete()
        management.call_command(
            self.command_name,
            "tests.pollwithexcludefields",
            auto=True,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        initial_history_record = PollWithExcludeFields.history.all()[0]
        self.assertEqual(initial_history_record.question, poll.question)


class TestCleanDuplicateHistory(TestCase):
    command_name = "clean_duplicate_history"
    command_error = (management.CommandError, SystemExit)

    def test_no_args(self):
        out = StringIO()
        management.call_command(self.command_name, stdout=out, stderr=StringIO())
        self.assertIn(clean_duplicate_history.Command.COMMAND_HINT, out.getvalue())

    def test_bad_args(self):
        test_data = (
            (clean_duplicate_history.Command.MODEL_NOT_HISTORICAL, ("tests.place",)),
            (clean_duplicate_history.Command.MODEL_NOT_FOUND, ("invalid.model",)),
            (clean_duplicate_history.Command.MODEL_NOT_FOUND, ("bad_key",)),
        )
        for msg, args in test_data:
            out = StringIO()
            self.assertRaises(
                self.command_error,
                management.call_command,
                self.command_name,
                *args,
                stdout=StringIO(),
                stderr=out
            )
            self.assertIn(msg, out.getvalue())

    def test_no_historical(self):
        out = StringIO()
        with replace_registry({"test_place": Place}):
            management.call_command(self.command_name, auto=True, stdout=out)
        self.assertIn(
            clean_duplicate_history.Command.NO_REGISTERED_MODELS, out.getvalue()
        )

    def test_auto_dry_run(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        p.save()

        # not related to dry_run test, just for increasing coverage :)
        # create instance with single-entry history older than "minutes"
        # so it is skipped
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        h = p.history.first()
        h.history_date -= timedelta(hours=1)
        h.save()

        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name,
            auto=True,
            minutes=50,
            dry=True,
            stdout=out,
            stderr=StringIO(),
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 3)

    def test_auto_cleanup(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        self.assertEqual(Poll.history.all().count(), 2)
        p.question = "Maybe this one won't...?"
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name, auto=True, stdout=out, stderr=StringIO()
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_verbose(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.question = "Maybe this one won't...?"
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name,
            "tests.poll",
            auto=True,
            verbosity=2,
            stdout=out,
            stderr=StringIO(),
        )
        self.assertEqual(
            out.getvalue(),
            "<class 'simple_history.tests.models.Poll'> has 3 historical entries\n"
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_dated(self):
        the_time_is_now = datetime.now()
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=the_time_is_now
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        p.question = "Or this one...?"
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 5)

        for h in Poll.history.all()[2:]:
            h.history_date -= timedelta(hours=1)
            h.save()

        management.call_command(
            self.command_name,
            auto=True,
            minutes=50,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        self.assertEqual(Poll.history.all().count(), 4)

    def test_auto_cleanup_dated_extra_one(self):
        the_time_is_now = datetime.now()
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=the_time_is_now
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        p.question = "Or this one...?"
        p.save()
        p.save()
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 7)

        for h in Poll.history.all()[2:]:
            h.history_date -= timedelta(hours=1)
            h.save()

        management.call_command(
            self.command_name,
            auto=True,
            minutes=50,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        # even though only the last 2 entries match the date range
        # the "extra_one" (the record before the oldest match)
        # is identical to the oldest match, so oldest match is deleted
        self.assertEqual(Poll.history.all().count(), 5)

    def test_auto_cleanup_custom_history_field(self):
        m = CustomManagerNameModel.objects.create(name="John")
        self.assertEqual(CustomManagerNameModel.log.all().count(), 1)
        m.save()
        self.assertEqual(CustomManagerNameModel.log.all().count(), 2)
        m.name = "Ivan"
        m.save()
        self.assertEqual(CustomManagerNameModel.log.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name, auto=True, stdout=out, stderr=StringIO()
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.CustomManagerNameModel'>\n",
        )
        self.assertEqual(CustomManagerNameModel.log.all().count(), 2)

    def test_auto_cleanup_with_excluded_fields(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.pub_date = p.pub_date + timedelta(days=1)
        p.save()
        self.assertEqual(Poll.history.all().count(), 2)
        out = StringIO()
        management.call_command(
            self.command_name,
            auto=True,
            excluded_fields=("pub_date",),
            stdout=out,
            stderr=StringIO(),
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 1)


class TestCleanOldHistory(TestCase):
    command_name = "clean_old_history"
    command_error = (management.CommandError, SystemExit)

    def test_no_args(self):
        out = StringIO()
        management.call_command(self.command_name, stdout=out, stderr=StringIO())
        self.assertIn(clean_old_history.Command.COMMAND_HINT, out.getvalue())

    def test_bad_args(self):
        test_data = (
            (clean_old_history.Command.MODEL_NOT_HISTORICAL, ("tests.place",)),
            (clean_old_history.Command.MODEL_NOT_FOUND, ("invalid.model",)),
            (clean_old_history.Command.MODEL_NOT_FOUND, ("bad_key",)),
        )
        for msg, args in test_data:
            out = StringIO()
            self.assertRaises(
                self.command_error,
                management.call_command,
                self.command_name,
                *args,
                stdout=StringIO(),
                stderr=out
            )
            self.assertIn(msg, out.getvalue())

    def test_no_historical(self):
        out = StringIO()
        with replace_registry({"test_place": Place}):
            management.call_command(self.command_name, auto=True, stdout=out)
        self.assertIn(clean_old_history.Command.NO_REGISTERED_MODELS, out.getvalue())

    def test_auto_dry_run(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        p.save()

        # not related to dry_run test, just for increasing coverage :)
        # create instance with single-entry history older than "minutes"
        # so it is skipped
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        h = p.history.first()
        h.history_date -= timedelta(days=31)
        h.save()

        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name,
            auto=True,
            days=20,
            dry=True,
            stdout=out,
            stderr=StringIO(),
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 3)

    def test_auto_cleanup(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        self.assertEqual(Poll.history.all().count(), 2)
        p.question = "Maybe this one won't...?"
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        h = p.history.first()
        h.history_date -= timedelta(days=40)
        h.save()
        management.call_command(
            self.command_name, auto=True, stdout=out, stderr=StringIO()
        )
        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_verbose(self):
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=datetime.now()
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.question = "Maybe this one won't...?"
        p.save()
        h = p.history.first()
        h.history_date -= timedelta(days=40)
        h.save()
        self.assertEqual(Poll.history.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name,
            "tests.poll",
            auto=True,
            verbosity=2,
            stdout=out,
            stderr=StringIO(),
        )

        self.assertEqual(
            out.getvalue(),
            "<class 'simple_history.tests.models.Poll'> has 1 old historical entries\n"
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.Poll'>\n",
        )
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_dated(self):
        the_time_is_now = datetime.now()
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=the_time_is_now
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        p.question = "Or this one...?"
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 5)

        for h in Poll.history.all()[2:]:
            h.history_date -= timedelta(days=30)
            h.save()

        management.call_command(
            self.command_name,
            auto=True,
            days=20,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_dated_extra_one(self):
        the_time_is_now = datetime.now()
        p = Poll.objects.create(
            question="Will this be deleted?", pub_date=the_time_is_now
        )
        self.assertEqual(Poll.history.all().count(), 1)
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 3)
        p.question = "Or this one...?"
        p.save()
        p.save()
        p.save()
        p.save()
        self.assertEqual(Poll.history.all().count(), 7)

        for h in Poll.history.all()[2:]:
            h.history_date -= timedelta(days=30)
            h.save()

        management.call_command(
            self.command_name,
            auto=True,
            days=20,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        # We will remove the 3 ones that we are marking as old
        self.assertEqual(Poll.history.all().count(), 2)

    def test_auto_cleanup_custom_history_field(self):
        m = CustomManagerNameModel.objects.create(name="John")
        self.assertEqual(CustomManagerNameModel.log.all().count(), 1)
        m.save()
        self.assertEqual(CustomManagerNameModel.log.all().count(), 2)
        m.name = "Ivan"
        m.save()
        h = m.log.first()
        h.history_date -= timedelta(days=40)
        h.save()
        self.assertEqual(CustomManagerNameModel.log.all().count(), 3)
        out = StringIO()
        management.call_command(
            self.command_name, auto=True, stdout=out, stderr=StringIO()
        )

        self.assertEqual(
            out.getvalue(),
            "Removed 1 historical records for "
            "<class 'simple_history.tests.models.CustomManagerNameModel'>\n",
        )
        self.assertEqual(CustomManagerNameModel.log.all().count(), 2)
