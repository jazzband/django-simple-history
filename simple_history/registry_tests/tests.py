from __future__ import unicode_literals

from datetime import datetime, timedelta
from six.moves import cStringIO as StringIO
import unittest

import django
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TestCase

from simple_history import exceptions, register
from ..tests.models import (
    Poll, Choice, Voter, Restaurant, HistoricalPoll, HistoricalChoice,
    HistoricalState, HistoricalCustomFKError,
    UserAccessorDefault, UserAccessorOverride,
    TrackedAbstractBaseA, TrackedAbstractBaseB,
    TrackedWithAbstractBase, TrackedWithConcreteBase,
    InheritTracking1, InheritTracking2, InheritTracking3, InheritTracking4,
)

try:
    from django.apps import apps
except ImportError:  # Django < 1.7
    from django.db.models import get_model
else:
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
        user = User.objects.create(username='bob', password='pass')
        self.assertEqual(len(User.histories.all()), 1)
        self.assertEqual(len(user.histories.all()), 1)

    def test_reregister(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):
            register(Restaurant, manager_name='again')

    def test_register_custome_records(self):
        self.assertEqual(len(Voter.history.all()), 0)
        poll = Poll.objects.create(pub_date=today)
        choice = Choice.objects.create(poll=poll, votes=0)
        user = User.objects.create(username='voter')
        voter = Voter.objects.create(choice=choice, user=user)
        self.assertEqual(len(voter.history.all()), 1)
        expected = 'Voter object changed by None as of '
        self.assertEqual(expected,
                         str(voter.history.all()[0])[:len(expected)])


class TestUserAccessor(unittest.TestCase):

    def test_accessor_default(self):
        register(UserAccessorDefault)
        assert not hasattr(User, 'historicaluseraccessordefault_set')

    def test_accessor_override(self):
        register(UserAccessorOverride,
                 user_related_name='my_history_model_accessor')
        assert hasattr(User, 'my_history_model_accessor')


class TestTrackingInheritance(TestCase):

    def test_tracked_abstract_base(self):
        self.assertEqual(
            [
                f.attname
                for f in TrackedWithAbstractBase.history.model._meta.fields
            ],
            [
                'id', 'history_id', 'history_date', 'history_user_id',
                'history_type',
            ],
        )

    def test_tracked_concrete_base(self):
        self.assertEqual(
            [
                f.attname
                for f in TrackedWithConcreteBase.history.model._meta.fields
            ],
            [
                'id', 'trackedconcretebase_ptr_id', 'history_id',
                'history_date', 'history_user_id', 'history_type',
            ],
        )

    def test_multiple_tracked_bases(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):
            class TrackedWithMultipleAbstractBases(
                    TrackedAbstractBaseA, TrackedAbstractBaseB):
                pass

    def test_tracked_abstract_and_untracked_concrete_base(self):
        self.assertEqual(
            [f.attname for f in InheritTracking1.history.model._meta.fields],
            [
                'id', 'untrackedconcretebase_ptr_id', 'history_id',
                'history_date', 'history_user_id', 'history_type',
            ],
        )

    def test_indirect_tracked_abstract_base(self):
        self.assertEqual(
            [f.attname for f in InheritTracking2.history.model._meta.fields],
            [
                'id', 'baseinherittracking2_ptr_id', 'history_id',
                'history_date', 'history_user_id', 'history_type',
            ],
        )

    def test_indirect_tracked_concrete_base(self):
        self.assertEqual(
            [f.attname for f in InheritTracking3.history.model._meta.fields],
            [
                'id', 'baseinherittracking3_ptr_id', 'history_id',
                'history_date', 'history_user_id', 'history_type',
            ],
        )

    def test_registering_with_tracked_abstract_base(self):
        with self.assertRaises(exceptions.MultipleRegistrationsError):
            register(InheritTracking4)


@unittest.skipUnless(django.get_version() >= "1.7", "Requires 1.7 migrations")
class TestMigrate(TestCase):

    def test_makemigration_command(self):
        management.call_command(
            'makemigrations', 'migration_test_app', stdout=StringIO())

    def test_migrate_command(self):
        management.call_command(
            'migrate', 'migration_test_app', fake=True, stdout=StringIO())
