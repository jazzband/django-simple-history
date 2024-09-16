import unittest
from datetime import datetime
from unittest import skipUnless
from unittest.mock import Mock, patch

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from simple_history.exceptions import AlternativeManagerError, NotHistoricalModelError
from simple_history.tests.models import (
    BulkCreateManyToManyModel,
    Document,
    Place,
    Poll,
    PollChildBookWithManyToMany,
    PollChildRestaurantWithManyToMany,
    PollWithAlternativeManager,
    PollWithExcludeFields,
    PollWithHistoricalSessionAttr,
    PollWithManyToMany,
    PollWithManyToManyCustomHistoryID,
    PollWithManyToManyWithIPAddress,
    PollWithSelfManyToMany,
    PollWithSeveralManyToMany,
    PollWithUniqueQuestion,
    Street,
)
from simple_history.utils import (
    bulk_create_with_history,
    bulk_update_with_history,
    get_history_manager_for_model,
    get_history_model_for_model,
    get_m2m_field_name,
    get_m2m_reverse_field_name,
    update_change_reason,
)

User = get_user_model()


class GetM2MFieldNamesTestCase(unittest.TestCase):
    def test__get_m2m_field_name__returns_expected_value(self):
        def field_names(model):
            history_model = get_history_model_for_model(model)
            # Sort the fields, to prevent flaky tests
            fields = sorted(history_model._history_m2m_fields, key=lambda f: f.name)
            return [get_m2m_field_name(field) for field in fields]

        self.assertListEqual(field_names(PollWithManyToMany), ["pollwithmanytomany"])
        self.assertListEqual(
            field_names(PollWithManyToManyCustomHistoryID),
            ["pollwithmanytomanycustomhistoryid"],
        )
        self.assertListEqual(
            field_names(PollWithManyToManyWithIPAddress),
            ["pollwithmanytomanywithipaddress"],
        )
        self.assertListEqual(
            field_names(PollWithSeveralManyToMany), ["pollwithseveralmanytomany"] * 3
        )
        self.assertListEqual(
            field_names(PollChildBookWithManyToMany),
            ["pollchildbookwithmanytomany"] * 2,
        )
        self.assertListEqual(
            field_names(PollChildRestaurantWithManyToMany),
            ["pollchildrestaurantwithmanytomany"] * 2,
        )
        self.assertListEqual(
            field_names(PollWithSelfManyToMany), ["from_pollwithselfmanytomany"]
        )

    def test__get_m2m_reverse_field_name__returns_expected_value(self):
        def field_names(model):
            history_model = get_history_model_for_model(model)
            # Sort the fields, to prevent flaky tests
            fields = sorted(history_model._history_m2m_fields, key=lambda f: f.name)
            return [get_m2m_reverse_field_name(field) for field in fields]

        self.assertListEqual(field_names(PollWithManyToMany), ["place"])
        self.assertListEqual(field_names(PollWithManyToManyCustomHistoryID), ["place"])
        self.assertListEqual(field_names(PollWithManyToManyWithIPAddress), ["place"])
        self.assertListEqual(
            field_names(PollWithSeveralManyToMany), ["book", "place", "restaurant"]
        )
        self.assertListEqual(
            field_names(PollChildBookWithManyToMany), ["book", "place"]
        )
        self.assertListEqual(
            field_names(PollChildRestaurantWithManyToMany), ["place", "restaurant"]
        )
        self.assertListEqual(
            field_names(PollWithSelfManyToMany), ["to_pollwithselfmanytomany"]
        )


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
        self.data_with_alternative_manager = [
            PollWithAlternativeManager(
                id=1, question="Question 1", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=2, question="Question 2", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=3, question="Question 3", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=4, question="Question 4", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=5, question="Question 5", pub_date=timezone.now()
            ),
        ]
        self.data_with_duplicates = [
            PollWithUniqueQuestion(
                pk=1, question="Question 1", pub_date=timezone.now()
            ),
            PollWithUniqueQuestion(
                pk=2, question="Question 2", pub_date=timezone.now()
            ),
            PollWithUniqueQuestion(
                pk=3, question="Question 1", pub_date=timezone.now()
            ),
        ]

    def test_bulk_create_history(self):
        bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 5)

    @override_settings(SIMPLE_HISTORY_ENABLED=False)
    def test_bulk_create_history_with_disabled_setting(self):
        bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 0)

    def test_bulk_create_history_alternative_manager(self):
        bulk_create_with_history(
            self.data,
            PollWithAlternativeManager,
        )

        self.assertEqual(PollWithAlternativeManager.all_objects.count(), 5)
        self.assertEqual(PollWithAlternativeManager.history.count(), 5)

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

    def test_bulk_create_history_with_default_date(self):
        date = datetime(2020, 7, 1)
        bulk_create_with_history(self.data, Poll, default_date=date)

        self.assertTrue(
            all([history.history_date == date for history in Poll.history.all()])
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

    def test_bulk_create_history_with_duplicates(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            bulk_create_with_history(
                self.data_with_duplicates,
                PollWithUniqueQuestion,
                ignore_conflicts=False,
            )

        self.assertEqual(PollWithUniqueQuestion.objects.count(), 0)
        self.assertEqual(PollWithUniqueQuestion.history.count(), 0)

    def test_bulk_create_history_with_duplicates_ignore_conflicts(self):
        bulk_create_with_history(
            self.data_with_duplicates, PollWithUniqueQuestion, ignore_conflicts=True
        )

        self.assertEqual(PollWithUniqueQuestion.objects.count(), 2)
        self.assertEqual(PollWithUniqueQuestion.history.count(), 2)

    def test_bulk_create_history_with_no_ids_return(self):
        pub_date = timezone.now()
        objects = [
            Poll(question="Question 1", pub_date=pub_date),
            Poll(question="Question 2", pub_date=pub_date),
            Poll(question="Question 3", pub_date=pub_date),
            Poll(question="Question 4", pub_date=pub_date),
            Poll(question="Question 5", pub_date=pub_date),
        ]

        _bulk_create = Poll._default_manager.bulk_create

        def mock_bulk_create(*args, **kwargs):
            _bulk_create(*args, **kwargs)
            return [
                Poll(question="Question 1", pub_date=pub_date),
                Poll(question="Question 2", pub_date=pub_date),
                Poll(question="Question 3", pub_date=pub_date),
                Poll(question="Question 4", pub_date=pub_date),
                Poll(question="Question 5", pub_date=pub_date),
            ]

        with patch.object(
            Poll._default_manager, "bulk_create", side_effect=mock_bulk_create
        ):
            with self.assertNumQueries(3):
                result = bulk_create_with_history(objects, Poll)
            self.assertEqual(
                [poll.question for poll in result], [poll.question for poll in objects]
            )
            self.assertNotEqual(result[0].id, None)


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
            _default_manager=Mock(
                bulk_create=Mock(return_value=[Place(name="Place 1")]),
                filter=Mock(return_value=Mock(order_by=Mock(return_value=objects))),
            ),
            _meta=Mock(get_fields=Mock(return_value=[])),
        )
        result = bulk_create_with_history(objects, model)
        self.assertEqual(result, objects)
        hist_manager_mock().bulk_history_create.assert_called_with(
            objects,
            batch_size=None,
            default_user=None,
            default_change_reason=None,
            default_date=None,
            custom_historical_attrs=None,
        )


class BulkCreateWithManyToManyField(TestCase):
    def setUp(self):
        self.data = [
            BulkCreateManyToManyModel(name="Object 1"),
            BulkCreateManyToManyModel(name="Object 2"),
            BulkCreateManyToManyModel(name="Object 3"),
            BulkCreateManyToManyModel(name="Object 4"),
            BulkCreateManyToManyModel(name="Object 5"),
        ]

    def test_bulk_create_with_history(self):
        bulk_create_with_history(self.data, BulkCreateManyToManyModel)

        self.assertEqual(BulkCreateManyToManyModel.objects.count(), 5)


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
            self.data,
            Poll,
            fields=["question"],
        )

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.objects.get(id=4).question, "Updated question")
        self.assertEqual(Poll.history.count(), 10)
        self.assertEqual(Poll.history.filter(history_type="~").count(), 5)

    @override_settings(SIMPLE_HISTORY_ENABLED=False)
    def test_bulk_update_history_without_history_enabled(self):
        self.assertEqual(Poll.history.count(), 5)
        # because setup called with enabled settings
        bulk_update_with_history(
            self.data,
            Poll,
            fields=["question"],
        )

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.objects.get(id=4).question, "Updated question")
        self.assertEqual(Poll.history.count(), 5)
        self.assertEqual(Poll.history.filter(history_type="~").count(), 0)

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

    def test_bulk_update_history_with_default_date(self):
        date = datetime(2020, 7, 1)
        bulk_update_with_history(
            self.data, Poll, fields=["question"], default_date=date
        )

        self.assertTrue(
            all(
                [
                    history.history_date == date
                    for history in Poll.history.filter(history_type="~")
                ]
            )
        )

    def test_bulk_update_history_num_queries_is_two(self):
        with self.assertNumQueries(2):
            bulk_update_with_history(
                self.data,
                Poll,
                fields=["question"],
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

    @skipUnless(django.VERSION >= (4, 0), "Requires Django 4.0 or above")
    def test_bulk_update_with_history_returns_rows_updated(self):
        rows_updated = bulk_update_with_history(
            self.data,
            Poll,
            fields=["question"],
        )
        self.assertEqual(rows_updated, 5)


class BulkUpdateWithHistoryAlternativeManagersTestCase(TestCase):
    def setUp(self):
        self.data = [
            PollWithAlternativeManager(
                id=1, question="Question 1", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=2, question="Question 2", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=3, question="Question 3", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=4, question="Question 4", pub_date=timezone.now()
            ),
            PollWithAlternativeManager(
                id=5, question="Question 5", pub_date=timezone.now()
            ),
        ]
        bulk_create_with_history(
            self.data,
            PollWithAlternativeManager,
        )

    def test_bulk_update_history_default_manager(self):
        self.data[3].question = "Updated question"

        bulk_update_with_history(
            self.data,
            PollWithAlternativeManager,
            fields=["question"],
        )

        self.assertEqual(PollWithAlternativeManager.all_objects.count(), 5)
        self.assertEqual(
            PollWithAlternativeManager.all_objects.get(id=4).question,
            "Updated question",
        )
        self.assertEqual(PollWithAlternativeManager.history.count(), 10)
        self.assertEqual(
            PollWithAlternativeManager.history.filter(history_type="~").count(), 5
        )

    def test_bulk_update_history_other_manager(self):
        # filtered by default manager
        self.data[0].question = "Updated question"

        bulk_update_with_history(
            self.data,
            PollWithAlternativeManager,
            fields=["question"],
            manager=PollWithAlternativeManager.all_objects,
        )

        self.assertEqual(PollWithAlternativeManager.all_objects.count(), 5)
        self.assertEqual(
            PollWithAlternativeManager.all_objects.get(id=1).question,
            "Updated question",
        )
        self.assertEqual(PollWithAlternativeManager.history.count(), 10)
        self.assertEqual(
            PollWithAlternativeManager.history.filter(history_type="~").count(), 5
        )

    def test_bulk_update_history_wrong_manager(self):
        with self.assertRaises(AlternativeManagerError):
            bulk_update_with_history(
                self.data,
                PollWithAlternativeManager,
                fields=["question"],
                manager=Poll.objects,
            )


class CustomHistoricalAttrsTest(TestCase):
    def setUp(self):
        self.data = [
            PollWithHistoricalSessionAttr(id=x, question=f"Question {x}")
            for x in range(1, 6)
        ]

    def test_bulk_create_history_with_custom_model_attributes(self):
        bulk_create_with_history(
            self.data,
            PollWithHistoricalSessionAttr,
            custom_historical_attrs={"session": "jam"},
        )

        self.assertEqual(PollWithHistoricalSessionAttr.objects.count(), 5)
        self.assertEqual(
            PollWithHistoricalSessionAttr.history.filter(session="jam").count(),
            5,
        )

    def test_bulk_update_history_with_custom_model_attributes(self):
        bulk_create_with_history(
            self.data,
            PollWithHistoricalSessionAttr,
            custom_historical_attrs={"session": None},
        )
        bulk_update_with_history(
            self.data,
            PollWithHistoricalSessionAttr,
            fields=[],
            custom_historical_attrs={"session": "training"},
        )

        self.assertEqual(PollWithHistoricalSessionAttr.objects.count(), 5)
        self.assertEqual(
            PollWithHistoricalSessionAttr.history.filter(session="training").count(),
            5,
        )

    def test_bulk_manager_with_custom_model_attributes(self):
        history_manager = get_history_manager_for_model(PollWithHistoricalSessionAttr)
        history_manager.bulk_history_create(
            self.data, custom_historical_attrs={"session": "co-op"}
        )

        self.assertEqual(PollWithHistoricalSessionAttr.objects.count(), 0)
        self.assertEqual(
            PollWithHistoricalSessionAttr.history.filter(session="co-op").count(),
            5,
        )


class UpdateChangeReasonTestCase(TestCase):
    def test_update_change_reason_with_excluded_fields(self):
        poll = PollWithExcludeFields(
            question="what's up?", pub_date=timezone.now(), place="The Pub"
        )
        poll.save()
        update_change_reason(poll, "Test change reason.")
        most_recent = poll.history.order_by("-history_date").first()
        self.assertEqual(most_recent.history_change_reason, "Test change reason.")
