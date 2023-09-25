from datetime import datetime, timedelta
from operator import attrgetter

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase, override_settings, skipUnlessDBFeature

from simple_history.manager import SIMPLE_HISTORY_REVERSE_ATTR_NAME

from ..models import Document, Poll, RankedDocument

User = get_user_model()


class AsOfTest(TestCase):
    model = Document

    def setUp(self):
        user = User.objects.create_user("tester", "tester@example.com")
        self.now = datetime.now()
        self.yesterday = self.now - timedelta(days=1)
        self.obj = self.model.objects.create()
        self.obj.changed_by = user
        self.obj.save()
        self.model.objects.all().delete()  # allows us to leave PK on instance
        (
            self.delete_history,
            self.change_history,
            self.create_history,
        ) = self.model.history.all()
        self.create_history.history_date = self.now - timedelta(days=2)
        self.create_history.save()
        self.change_history.history_date = self.now - timedelta(days=1)
        self.change_history.save()
        self.delete_history.history_date = self.now
        self.delete_history.save()

    def test_created_after(self):
        """An object created after the 'as of' date should not be
        included.

        """
        as_of_list = list(self.model.history.as_of(self.now - timedelta(days=5)))
        self.assertFalse(as_of_list)

    def test_deleted_before(self):
        """An object deleted before the 'as of' date should not be
        included.

        """
        as_of_list = list(self.model.history.as_of(self.now + timedelta(days=1)))
        self.assertFalse(as_of_list)

    def test_deleted_after(self):
        """An object created before, but deleted after the 'as of'
        date should be included.

        """
        as_of_list = list(self.model.history.as_of(self.now - timedelta(days=1)))
        self.assertEqual(len(as_of_list), 1)
        self.assertEqual(as_of_list[0].pk, self.obj.pk)

    def test_modified(self):
        """An object modified before the 'as of' date should reflect
        the last version.

        """
        as_of_list = list(self.model.history.as_of(self.now - timedelta(days=1)))
        self.assertEqual(as_of_list[0].changed_by, self.obj.changed_by)


class AsOfAdditionalTestCase(TestCase):
    def test_create_and_delete(self):
        document = Document.objects.create()
        now = datetime.now()
        document.delete()

        docs_as_of_now = Document.history.as_of(now)
        doc = docs_as_of_now[0]
        # as_of queries inject a property allowing callers
        # to go from instance to historical instance
        historic = getattr(doc, SIMPLE_HISTORY_REVERSE_ATTR_NAME)
        self.assertIsNotNone(historic)
        # as_of queries inject the time point of the original
        # query into the historic record so callers can do magical
        # things like chase historic foreign key relationships
        # by patching forward and reverse one-to-one relationship
        # processing (see issue 880)
        self.assertEqual(historic._as_of, now)

        docs_as_of_tmw = Document.history.as_of(now + timedelta(days=1))
        with self.assertNumQueries(1):
            self.assertFalse(list(docs_as_of_tmw))

    def test_multiple(self):
        document1 = Document.objects.create()
        document2 = Document.objects.create()
        historical = Document.history.as_of(datetime.now() + timedelta(days=1))
        # history, even converted to objects, is kept in reverse chronological order
        # because sorting it based on the original table's meta ordering is not possible
        # when the ordering leverages foreign key relationships
        with self.assertNumQueries(1):
            self.assertEqual(list(historical), [document2, document1])

    def test_filter_pk_as_instance(self):
        # when a queryset is returning historical documents, `pk` queries
        # reference the history_id; however when a queryset is returning
        # instances, `pk' queries reference the original table's primary key
        document1 = RankedDocument.objects.create(id=101, rank=42)
        RankedDocument.objects.create(id=102, rank=84)
        self.assertFalse(RankedDocument.history.filter(pk=document1.id))
        self.assertTrue(
            RankedDocument.history.all().as_instances().filter(pk=document1.id)
        )

    def test_as_of(self):
        """Demonstrates how as_of works now that it returns a QuerySet."""
        t0 = datetime.now()
        document1 = RankedDocument.objects.create(rank=42)
        document2 = RankedDocument.objects.create(rank=84)
        t1 = datetime.now()
        document2.rank = 51
        document2.save()
        document1.delete()
        t2 = datetime.now()

        # nothing exists at t0
        queryset = RankedDocument.history.as_of(t0)
        self.assertEqual(queryset.count(), 0)

        # at t1, two records exist
        queryset = RankedDocument.history.as_of(t1)
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(rank__gte=75).count(), 1)
        ids = {item["id"] for item in queryset.values("id")}
        self.assertEqual(ids, {document1.id, document2.id})

        # these records are historic
        record = queryset[0]
        historic = getattr(record, SIMPLE_HISTORY_REVERSE_ATTR_NAME)
        self.assertIsInstance(historic, RankedDocument.history.model)
        self.assertEqual(historic._as_of, t1)

        # at t2 we have one record left
        queryset = RankedDocument.history.as_of(t2)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.filter(rank__gte=75).count(), 0)

    def test_historical_query_set(self):
        """
        Demonstrates how the HistoricalQuerySet works to provide as_of functionality.
        """
        document1 = RankedDocument.objects.create(rank=42)
        document2 = RankedDocument.objects.create(rank=84)
        document2.rank = 51
        document2.save()
        document1.delete()
        t2 = datetime.now()

        # look for historical records, get back a queryset
        with self.assertNumQueries(1):
            queryset = RankedDocument.history.filter(history_date__lte=t2)
            self.assertEqual(queryset.count(), 4)

        # only want the most recend records (provided by HistoricalQuerySet)
        self.assertEqual(queryset.latest_of_each().count(), 2)

        # want to see the instances as of that time?
        self.assertEqual(queryset.latest_of_each().as_instances().count(), 1)

        # these new methods are idempotent
        self.assertEqual(
            queryset.latest_of_each()
            .latest_of_each()
            .as_instances()
            .as_instances()
            .count(),
            1,
        )

        # that was all the same as calling as_of!
        self.assertEqual(
            set(
                RankedDocument.history.filter(history_date__lte=t2)
                .latest_of_each()
                .as_instances()
            ),
            set(RankedDocument.history.as_of(t2)),
        )


class BulkHistoryCreateTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=datetime.now()),
            Poll(id=2, question="Question 2", pub_date=datetime.now()),
            Poll(id=3, question="Question 3", pub_date=datetime.now()),
            Poll(id=4, question="Question 4", pub_date=datetime.now()),
        ]

    # DEV: Remove this method when the minimum required Django version is 4.2
    def assertQuerySetEqual(self, *args, **kwargs):
        if django.VERSION < (4, 2):
            return self.assertQuerysetEqual(*args, **kwargs)
        else:
            return super().assertQuerySetEqual(*args, **kwargs)

    def test_simple_bulk_history_create(self):
        created = Poll.history.bulk_history_create(self.data)
        self.assertEqual(len(created), 4)
        self.assertQuerySetEqual(
            Poll.history.order_by("question"),
            ["Question 1", "Question 2", "Question 3", "Question 4"],
            attrgetter("question"),
        )
        self.assertTrue(
            all([history.history_type == "+" for history in Poll.history.all()])
        )

        created = Poll.history.bulk_create([])
        self.assertEqual(created, [])
        self.assertEqual(Poll.history.count(), 4)

    @override_settings(SIMPLE_HISTORY_ENABLED=False)
    def test_simple_bulk_history_create_without_history_enabled(self):
        Poll.history.bulk_history_create(self.data)
        self.assertEqual(Poll.history.count(), 0)

    def test_bulk_history_create_with_change_reason(self):
        for poll in self.data:
            poll._change_reason = "reason"

        Poll.history.bulk_history_create(self.data)

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "reason"
                    for history in Poll.history.all()
                ]
            )
        )

    def test_bulk_history_create_with_default_user(self):
        user = User.objects.create_user("tester", "tester@example.com")

        Poll.history.bulk_history_create(self.data, default_user=user)

        self.assertTrue(
            all([history.history_user == user for history in Poll.history.all()])
        )

    def test_bulk_history_create_with_default_change_reason(self):
        Poll.history.bulk_history_create(self.data, default_change_reason="test")

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "test"
                    for history in Poll.history.all()
                ]
            )
        )

    def test_bulk_history_create_history_user_overrides_default(self):
        user1 = User.objects.create_user("tester1", "tester1@example.com")
        user2 = User.objects.create_user("tester2", "tester2@example.com")

        for data in self.data:
            data._history_user = user1

        Poll.history.bulk_history_create(self.data, default_user=user2)

        self.assertTrue(
            all([history.history_user == user1 for history in Poll.history.all()])
        )

    def test_bulk_history_create_change_reason_overrides_default(self):
        for data in self.data:
            data._change_reason = "my_reason"

        Poll.history.bulk_history_create(self.data, default_change_reason="test")

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "my_reason"
                    for history in Poll.history.all()
                ]
            )
        )

    def test_bulk_history_create_on_objs_without_ids(self):
        self.data = [
            Poll(question="Question 1", pub_date=datetime.now()),
            Poll(question="Question 2", pub_date=datetime.now()),
            Poll(question="Question 3", pub_date=datetime.now()),
            Poll(question="Question 4", pub_date=datetime.now()),
        ]

        with self.assertRaises(IntegrityError):
            Poll.history.bulk_history_create(self.data)

    def test_set_custom_history_date_on_first_obj(self):
        self.data[0]._history_date = datetime(2000, 1, 1)

        Poll.history.bulk_history_create(self.data)

        self.assertEqual(
            Poll.history.order_by("question")[0].history_date, datetime(2000, 1, 1)
        )

    def test_set_custom_history_user_on_first_obj(self):
        user = User.objects.create_user("tester", "tester@example.com")
        self.data[0]._history_user = user

        Poll.history.bulk_history_create(self.data)

        self.assertEqual(Poll.history.order_by("question")[0].history_user, user)

    @skipUnlessDBFeature("has_bulk_insert")
    def test_efficiency(self):
        with self.assertNumQueries(1):
            Poll.history.bulk_history_create(self.data)


class BulkHistoryUpdateTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=datetime.now()),
            Poll(id=2, question="Question 2", pub_date=datetime.now()),
            Poll(id=3, question="Question 3", pub_date=datetime.now()),
            Poll(id=4, question="Question 4", pub_date=datetime.now()),
        ]

    # DEV: Remove this method when the minimum required Django version is 4.2
    def assertQuerySetEqual(self, *args, **kwargs):
        if django.VERSION < (4, 2):
            return self.assertQuerysetEqual(*args, **kwargs)
        else:
            return super().assertQuerySetEqual(*args, **kwargs)

    def test_simple_bulk_history_create(self):
        created = Poll.history.bulk_history_create(self.data, update=True)
        self.assertEqual(len(created), 4)
        self.assertQuerySetEqual(
            Poll.history.order_by("question"),
            ["Question 1", "Question 2", "Question 3", "Question 4"],
            attrgetter("question"),
        )
        self.assertTrue(
            all([history.history_type == "~" for history in Poll.history.all()])
        )

        created = Poll.history.bulk_create([])
        self.assertEqual(created, [])
        self.assertEqual(Poll.history.count(), 4)

    def test_bulk_history_create_with_change_reason(self):
        for poll in self.data:
            poll._change_reason = "reason"

        Poll.history.bulk_history_create(self.data)

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "reason"
                    for history in Poll.history.all()
                ]
            )
        )
