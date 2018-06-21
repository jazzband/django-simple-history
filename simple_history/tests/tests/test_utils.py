from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import now
from mock import Mock, patch

from simple_history.exceptions import NotHistoricalModelError
from simple_history.tests.models import (
    Document,
    Place,
    Poll,
    PollWithExcludeFields
)
from simple_history.utils import bulk_create_with_history


class BulkCreateWithHistoryTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question='Question 1', pub_date=now()),
            Poll(id=2, question='Question 2', pub_date=now()),
            Poll(id=3, question='Question 3', pub_date=now()),
            Poll(id=4, question='Question 4', pub_date=now()),
            Poll(id=5, question='Question 5', pub_date=now()),
        ]

    def test_bulk_create_history(self):
        bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 5)

    def test_bulk_create_history_num_queries_is_two(self):
        with self.assertNumQueries(2):
            bulk_create_with_history(self.data, Poll)

    def test_bulk_create_history_on_model_without_history_raises_error(self):
        self.data = [
            Place(id=1, name='Place 1'),
            Place(id=2, name='Place 2'),
            Place(id=3, name='Place 3'),
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
        bulk_create_with_history(self.data, PollWithExcludeFields)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertEqual(Poll.history.count(), 0)

        self.assertEqual(PollWithExcludeFields.objects.count(), 5)
        self.assertEqual(PollWithExcludeFields.history.count(), 5)


class BulkCreateWithHistoryTransactionTestCase(TransactionTestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question='Question 1', pub_date=now()),
            Poll(id=2, question='Question 2', pub_date=now()),
            Poll(id=3, question='Question 3', pub_date=now()),
            Poll(id=4, question='Question 4', pub_date=now()),
            Poll(id=5, question='Question 5', pub_date=now()),
        ]

    @patch('simple_history.manager.HistoryManager.bulk_history_create',
           Mock(side_effect=Exception))
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
        Poll.objects.create(id=5, question='Question 5', pub_date=now())

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
