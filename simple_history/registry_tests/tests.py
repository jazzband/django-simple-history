import unittest
import uuid
from datetime import datetime, timedelta
from io import StringIO

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TestCase, TransactionTestCase, override_settings

from simple_history import exceptions, register

from ..tests.models import (
    Choice,
    InheritTracking1,
    InheritTracking2,
    InheritTracking3,
    InheritTracking4,
    ModelWithCustomAttrForeignKey,
    ModelWithCustomAttrOneToOneField,
    ModelWithHistoryInDifferentApp,
    Poll,
    Restaurant,
    TrackedAbstractBaseA,
    TrackedAbstractBaseB,
    TrackedWithAbstractBase,
    TrackedWithConcreteBase,
    UserAccessorDefault,
    UserAccessorOverride,
    UUIDRegisterModel,
    Voter,
)

get_model = apps.get_model
User = get_user_model()
today = datetime(2021, 1, 1, 10, 0)
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


class RegisterTest(TestCase):
    def test_register_no_args(self):
        self.assertEqual(len(Choice.history.all()), 0)
        poll = Poll.objects.create(pub_date=today)
        choice = Choice.objects.create(poll=poll, votes=0)
        self.assertEqual(len(choice.history.all()), 1)

    def test_register_separate_app(self):
        def get_history(model):
            return model.history

        self.assertRaises(AttributeError, get_history, User)
        self.assertEqual(len(User.histories.all()), 0)
        user = User.objects.create(username="bob", password="pass")
        self.assertEqual(len(User.histories.all()), 1)
        self.assertEqual(len(user.histories.all()), 1)

    def test_reregister(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):
            register(Restaurant, manager_name="again")

    def test_register_custome_records(self):
        self.assertEqual(len(Voter.history.all()), 0)
        poll = Poll.objects.create(pub_date=today)
        choice = Choice.objects.create(poll=poll, votes=0)
        user = User.objects.create(username="voter")
        voter = Voter.objects.create(choice=choice, user=user)
        self.assertEqual(len(voter.history.all()), 1)
        expected = "Voter object changed by None as of "
        self.assertEqual(expected, str(voter.history.all()[0])[: len(expected)])

    def test_register_history_id_field(self):
        self.assertEqual(len(UUIDRegisterModel.history.all()), 0)
        entry = UUIDRegisterModel.objects.create()
        self.assertEqual(len(entry.history.all()), 1)
        history = entry.history.all()[0]
        self.assertTrue(isinstance(history.history_id, uuid.UUID))


class TestUserAccessor(unittest.TestCase):
    def test_accessor_default(self):
        register(UserAccessorDefault)
        self.assertFalse(hasattr(User, "historicaluseraccessordefault_set"))

    def test_accessor_override(self):
        register(UserAccessorOverride, user_related_name="my_history_model_accessor")
        self.assertTrue(hasattr(User, "my_history_model_accessor"))


class TestInheritedModule(TestCase):
    def test_using_app_label(self):
        try:
            from ..tests.models import HistoricalConcreteExternal
        except ImportError:
            self.fail("HistoricalConcreteExternal is in wrong module")

    def test_default(self):
        try:
            from ..tests.models import HistoricalConcreteExternal2
        except ImportError:
            self.fail("HistoricalConcreteExternal2 is in wrong module")


class TestTrackingInheritance(TestCase):
    def test_tracked_abstract_base(self):
        self.assertEqual(
            sorted(
                f.attname for f in TrackedWithAbstractBase.history.model._meta.fields
            ),
            sorted(
                [
                    "id",
                    "history_id",
                    "history_change_reason",
                    "history_date",
                    "history_user_id",
                    "history_type",
                ]
            ),
        )

    def test_tracked_concrete_base(self):
        self.assertEqual(
            sorted(
                f.attname for f in TrackedWithConcreteBase.history.model._meta.fields
            ),
            sorted(
                [
                    "id",
                    "trackedconcretebase_ptr_id",
                    "history_id",
                    "history_change_reason",
                    "history_date",
                    "history_user_id",
                    "history_type",
                ]
            ),
        )

    def test_multiple_tracked_bases(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):

            class TrackedWithMultipleAbstractBases(
                TrackedAbstractBaseA, TrackedAbstractBaseB
            ):
                pass

    def test_tracked_abstract_and_untracked_concrete_base(self):
        self.assertEqual(
            sorted(f.attname for f in InheritTracking1.history.model._meta.fields),
            sorted(
                [
                    "id",
                    "untrackedconcretebase_ptr_id",
                    "history_id",
                    "history_change_reason",
                    "history_date",
                    "history_user_id",
                    "history_type",
                ]
            ),
        )

    def test_indirect_tracked_abstract_base(self):
        self.assertEqual(
            sorted(f.attname for f in InheritTracking2.history.model._meta.fields),
            sorted(
                [
                    "id",
                    "baseinherittracking2_ptr_id",
                    "history_id",
                    "history_change_reason",
                    "history_date",
                    "history_user_id",
                    "history_type",
                ]
            ),
        )

    def test_indirect_tracked_concrete_base(self):
        self.assertEqual(
            sorted(f.attname for f in InheritTracking3.history.model._meta.fields),
            sorted(
                [
                    "id",
                    "baseinherittracking3_ptr_id",
                    "history_id",
                    "history_change_reason",
                    "history_date",
                    "history_user_id",
                    "history_type",
                ]
            ),
        )

    def test_registering_with_tracked_abstract_base(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):
            register(InheritTracking4)


class TestCustomAttrForeignKey(TestCase):
    """https://github.com/django-commons/django-simple-history/issues/431"""

    def test_custom_attr(self):
        field = ModelWithCustomAttrForeignKey.history.model._meta.get_field("poll")
        self.assertEqual(field.attr_name, "custom_poll")


class TestCustomAttrOneToOneField(TestCase):
    """https://github.com/django-commons/django-simple-history/issues/870"""

    def test_custom_attr(self):
        field = ModelWithCustomAttrOneToOneField.history.model._meta.get_field("poll")
        self.assertFalse(hasattr(field, "attr_name"))


@override_settings(MIGRATION_MODULES={})
class TestMigrate(TransactionTestCase):
    def test_makemigration_command(self):
        management.call_command(
            "makemigrations", "migration_test_app", stdout=StringIO()
        )

    def test_migrate_command(self):
        management.call_command(
            "migrate", "migration_test_app", fake=True, stdout=StringIO()
        )


class TestModelWithHistoryInDifferentApp(TestCase):
    """https://github.com/django-commons/django-simple-history/issues/485"""

    def test__different_app(self):
        appLabel = ModelWithHistoryInDifferentApp.history.model._meta.app_label
        self.assertEqual(appLabel, "external")
