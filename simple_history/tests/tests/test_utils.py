from unittest import skipIf

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from mock import Mock, patch

from simple_history.exceptions import NotHistoricalModelError
from simple_history.tests.models import (
    Document,
    Place,
    Poll,
    PollWithExcludeFields,
    Street,
)
from simple_history.utils import (
    bulk_create_with_history,
    update_change_reason,
    bulk_update_with_history,
)

User = get_user_model()


class BulkCreateWithHistoryTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=timezone.now()),
            Poll(id=2, question="Question 2", pub_date=timezone.now()),
            Poll(id=3, question="Question 3", pub_date=timezone.now()),
            Poll(id=4, question="Question 4", pub_date=timezone.now()),
            Poll(id=5, question="Question 5", pub_date=timezone.now()),
        ]
        self.data_with_excluded_fields = [
            PollWithExcludeFields(id=1, question="Question 1", pub_date=timezone.now()),
            PollWithExcludeFields(id=2, question="Question 2", pub_date=timezone.now()),
            PollWithExcludeFields(id=3, question="Question 3", pub_date=timezone.now()),
            PollWithExcludeFields(id=4, question="Question 4", pub_date=timezone.now()),
            PollWithExcludeFields(id=5, question="Question 5", pub_date=timezone.now()),
        ]

    def test_bulk_create_history(self):
        bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 5)

    def test_bulk_create_history_with_default_user(self):
        user = User.objects.create_user("tester", "tester@example.com")

        bulk_create_with_history(self.data, Poll, default_user=user)

        self.assertTrue(
            all([history.history_user == user for history in Poll.history.all()])
        )

    def test_bulk_create_history_with_default_change_reason(self):
        bulk_create_with_history(
            self.data, Poll, default_change_reason="my change reason"
        )

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "my change reason"
                    for history in Poll.history.all()
                ]
            )
        )

    def test_bulk_create_history_num_queries_is_two(self):
        with self.assertNumQueries(2):
            bulk_create_with_history(self.data, Poll)

    def test_bulk_create_history_on_model_without_history_raises_error(self):
        self.data = [
            Place(id=1, name="Place 1"),
            Place(id=2, name="Place 2"),
            Place(id=3, name="Place 3"),
        ]
        with self.assertRaises(NotHistoricalModelError):
            bulk_create_with_history(self.data, Place)

    def test_num_queries_when_batch_size_is_less_than_total(self):
        with self.assertNumQueries(6):
            bulk_create_with_history(self.data, Poll, batch_size=2)

    def test_bulk_create_history_with_batch_size(self):
        bulk_create_with_history(self.data, Poll, batch_size=2)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 5)

    def test_bulk_create_works_with_excluded_fields(self):
        bulk_create_with_history(self.data_with_excluded_fields, PollWithExcludeFields)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertEqual(Poll.history.count(), 0)

        self.assertEqual(PollWithExcludeFields.objects.count(), 5)
        self.assertEqual(PollWithExcludeFields.history.count(), 5)

    def test_bulk_create_history_with_relation_name(self):
        self.data = [
            Street(name="Street 1"),
            Street(name="Street 2"),
            Street(name="Street 3"),
            Street(name="Street 4"),
        ]
        bulk_create_with_history(self.data, Street)
        self.assertEqual(Street.objects.count(), 4)
        self.assertEqual(Street.log.count(), 4)


class BulkCreateWithHistoryTransactionTestCase(TransactionTestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=timezone.now()),
            Poll(id=2, question="Question 2", pub_date=timezone.now()),
            Poll(id=3, question="Question 3", pub_date=timezone.now()),
            Poll(id=4, question="Question 4", pub_date=timezone.now()),
            Poll(id=5, question="Question 5", pub_date=timezone.now()),
        ]

    @patch(
        "simple_history.manager.HistoryManager.bulk_history_create",
        Mock(side_effect=Exception),
    )
    def test_transaction_rolls_back_if_bulk_history_create_fails(self):
        with self.assertRaises(Exception):
            bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertEqual(Poll.history.count(), 0)

    def test_bulk_create_history_on_objects_that_already_exist(self):
        Poll.objects.bulk_create(self.data)

        with self.assertRaises(IntegrityError):
            bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 0)

    def test_bulk_create_history_rolls_back_when_last_exists(self):
        Poll.objects.create(id=5, question="Question 5", pub_date=timezone.now())

        self.assertEqual(Poll.objects.count(), 1)
        self.assertEqual(Poll.history.count(), 1)

        with self.assertRaises(IntegrityError):
            bulk_create_with_history(self.data, Poll, batch_size=1)

        self.assertEqual(Poll.objects.count(), 1)
        self.assertEqual(Poll.history.count(), 1)

    def test_bulk_create_fails_with_wrong_model(self):
        with self.assertRaises(AttributeError):
            bulk_create_with_history(self.data, Document)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertEqual(Poll.history.count(), 0)

    @patch("simple_history.utils.get_history_manager_for_model")
    def test_bulk_create_no_ids_return(self, hist_manager_mock):
        objects = [Place(id=1, name="Place 1")]
        model = Mock(
            objects=Mock(
                bulk_create=Mock(return_value=[Place(name="Place 1")]),
                filter=Mock(return_value=objects),
            )
        )
        result = bulk_create_with_history(objects, model)
        self.assertEqual(result, objects)
        hist_manager_mock().bulk_history_create.assert_called_with(
            objects, batch_size=None, default_user=None, default_change_reason=None
        )


@skipIf(django.VERSION < (2, 2,), reason="bulk_update does not exist before 2.2")
class BulkUpdateWithHistoryTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question="Question 1", pub_date=timezone.now()),
            Poll(id=2, question="Question 2", pub_date=timezone.now()),
            Poll(id=3, question="Question 3", pub_date=timezone.now()),
            Poll(id=4, question="Question 4", pub_date=timezone.now()),
            Poll(id=5, question="Question 5", pub_date=timezone.now()),
        ]
        bulk_create_with_history(self.data, Poll)

        self.data[3].question = "Updated question"

    def test_bulk_update_history(self):
        bulk_update_with_history(
            self.data, Poll, fields=["question"],
        )

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.objects.get(id=4).question, "Updated question")
        self.assertEqual(Poll.history.count(), 10)
        self.assertEqual(Poll.history.filter(history_type="~").count(), 5)

    def test_bulk_update_history_with_default_user(self):
        user = User.objects.create_user("tester", "tester@example.com")

        bulk_update_with_history(
            self.data, Poll, fields=["question"], default_user=user
        )

        self.assertTrue(
            all(
                [
                    history.history_user == user
                    for history in Poll.history.filter(history_type="~")
                ]
            )
        )

    def test_bulk_update_history_with_default_change_reason(self):
        bulk_update_with_history(
            self.data,
            Poll,
            fields=["question"],
            default_change_reason="my change reason",
        )

        self.assertTrue(
            all(
                [
                    history.history_change_reason == "my change reason"
                    for history in Poll.history.filter(history_type="~")
                ]
            )
        )

    def test_bulk_update_history_num_queries_is_two(self):
        with self.assertNumQueries(2):
            bulk_update_with_history(
                self.data, Poll, fields=["question"],
            )

    def test_bulk_update_history_on_model_without_history_raises_error(self):
        self.data = [
            Place(id=1, name="Place 1"),
            Place(id=2, name="Place 2"),
            Place(id=3, name="Place 3"),
        ]
        Place.objects.bulk_create(self.data)
        self.data[0].name = "test"

        with self.assertRaises(NotHistoricalModelError):
            bulk_update_with_history(self.data, Place, fields=["name"])

    def test_num_queries_when_batch_size_is_less_than_total(self):
        with self.assertNumQueries(6):
            bulk_update_with_history(self.data, Poll, fields=["question"], batch_size=2)

    def test_bulk_update_history_with_batch_size(self):
        bulk_update_with_history(self.data, Poll, fields=["question"], batch_size=2)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.filter(history_type="~").count(), 5)


class UpdateChangeReasonTestCase(TestCase):
    def test_update_change_reason_with_excluded_fields(self):
        poll = PollWithExcludeFields(
            question="what's up?", pub_date=timezone.now(), place="The Pub"
        )
        poll.save()
        update_change_reason(poll, "Test change reason.")
        most_recent = poll.history.order_by("-history_date").first()
        self.assertEqual(most_recent.history_change_reason, "Test change reason.")
