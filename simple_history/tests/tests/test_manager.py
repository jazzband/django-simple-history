from datetime import datetime, timedelta
from operator import attrgetter

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase, skipUnlessDBFeature

from simple_history.exceptions import CannotSwitchQuerySetResultTypeError

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
        now = datetime.now()
        document = Document.objects.create()
        document.delete()
        for doc_change in Document.history.all():
            doc_change.history_date = now
            doc_change.save()
        docs_as_of_tmw = Document.history.as_of(now + timedelta(days=1))
        self.assertFalse(list(docs_as_of_tmw))

    def test_multiple(self):
        document1 = RankedDocument.objects.create(rank=25)
        document2 = RankedDocument.objects.create(rank=75)
        foo = RankedDocument.history.filter(as_of=datetime.now() + timedelta(days=1))
        historical = RankedDocument.history.as_of(datetime.now() + timedelta(days=1))
        self.assertEqual(list(historical), [document1, document2])

        # you can pass additional filter arguments into as_of
        historical = RankedDocument.history.as_of(
            datetime.now() + timedelta(days=1), rank__gte=50
        )
        self.assertEqual(list(historical), [document2])

        # if you query against as_of with None, it gets all historic records
        historical = RankedDocument.history.filter(as_of=None)
        self.assertEqual(len(historical), 2)
        self.assertNotEqual(RankedDocument.history.model, RankedDocument)
        self.assertEqual(
            [item.__class__ for item in historical],
            [RankedDocument.history.model, RankedDocument.history.model],
        )

        # if you query with as_of set to a time point, you get historical records
        historical = RankedDocument.history.filter(
            as_of=datetime.now() + timedelta(days=1)
        )
        self.assertEqual(len(historical), 2)
        self.assertNotEqual(RankedDocument.history.model, RankedDocument)
        self.assertEqual(
            [item.__class__ for item in historical],
            [RankedDocument.history.model, RankedDocument.history.model],
        )

        # note: you cannot call as_original() after the queryset has fetched
        with self.assertRaises(CannotSwitchQuerySetResultTypeError):
            historical.as_original()

        # use as_original to get a HistoryQuerySet that generates genuine RankedDocument(s)
        # instead of historical records
        genuine = RankedDocument.history.filter(
            as_of=datetime.now() + timedelta(days=1), rank__lte=50
        ).as_original()
        self.assertEqual(len(genuine), 1)
        self.assertEqual([item.__class__ for item in genuine], [RankedDocument])
        self.assertEqual(list(genuine)[0].rank, 25)


class BulkHistoryCreateTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=datetime.now()),
            Poll(id=2, question="Question 2", pub_date=datetime.now()),
            Poll(id=3, question="Question 3", pub_date=datetime.now()),
            Poll(id=4, question="Question 4", pub_date=datetime.now()),
        ]

    def test_simple_bulk_history_create(self):
        created = Poll.history.bulk_history_create(self.data)
        self.assertEqual(len(created), 4)
        self.assertQuerysetEqual(
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

    def test_simple_bulk_history_create(self):
        created = Poll.history.bulk_history_create(self.data, update=True)
        self.assertEqual(len(created), 4)
        self.assertQuerysetEqual(
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
