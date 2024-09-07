import unittest
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Final, List, Optional, Type, Union
from unittest import skipUnless
from unittest.mock import ANY, Mock, patch

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Model
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from simple_history.exceptions import AlternativeManagerError, NotHistoricalModelError
from simple_history.manager import HistoryManager
from simple_history.models import HistoricalChanges, HistoricalRecords
from simple_history.utils import (
    DisableHistoryInfo,
    _StoredDisableHistoryInfo,
    bulk_create_with_history,
    bulk_update_with_history,
    disable_history,
    get_historical_records_of_instance,
    get_history_manager_for_model,
    get_history_model_for_model,
    get_m2m_field_name,
    get_m2m_reverse_field_name,
    get_pk_name,
    is_history_disabled,
    update_change_reason,
)

from ..external import models as external
from ..models import (
    AbstractBase,
    AbstractModelCallable1,
    BaseModel,
    Book,
    BulkCreateManyToManyModel,
    Choice,
    ConcreteAttr,
    ConcreteExternal,
    ConcreteUtil,
    Contact,
    ContactRegister,
    CustomManagerNameModel,
    Document,
    ExternalModelSpecifiedWithAppParam,
    ExternalModelWithAppLabel,
    FirstLevelInheritedModel,
    HardbackBook,
    HistoricalBook,
    HistoricalPoll,
    HistoricalPollInfo,
    InheritTracking1,
    ModelWithHistoryInDifferentApp,
    ModelWithHistoryUsingBaseModelDb,
    OverrideModelNameAsCallable,
    OverrideModelNameRegisterMethod1,
    OverrideModelNameUsingBaseModel1,
    Place,
    Poll,
    PollChildBookWithManyToMany,
    PollChildRestaurantWithManyToMany,
    PollInfo,
    PollParentWithManyToMany,
    PollWithAlternativeManager,
    PollWithCustomManager,
    PollWithExcludedFKField,
    PollWithExcludeFields,
    PollWithHistoricalSessionAttr,
    PollWithManyToMany,
    PollWithManyToManyCustomHistoryID,
    PollWithManyToManyWithIPAddress,
    PollWithQuerySetCustomizations,
    PollWithSelfManyToMany,
    PollWithSeveralManyToMany,
    PollWithUniqueQuestion,
    Profile,
    Restaurant,
    Street,
    TestHistoricParticipanToHistoricOrganization,
    TestOrganizationWithHistory,
    TestParticipantToHistoricOrganization,
    TrackedAbstractBaseA,
    TrackedConcreteBase,
    TrackedWithAbstractBase,
    TrackedWithConcreteBase,
    Voter,
)
from .utils import HistoricalTestCase

User = get_user_model()


class DisableHistoryTestCase(HistoricalTestCase):
    """Tests related to the ``disable_history()`` context manager."""

    def test_disable_history_info(self):
        """Test that the various utilities for checking the current info on how
        historical record creation is disabled, return the expected values.
        This includes ``DisableHistoryInfo`` and ``is_history_disabled()``, as well as
        the ``_StoredDisableHistoryInfo`` stored through ``HistoricalRecords.context``.
        """

        class DisableHistoryMode(Enum):
            NOT_DISABLED = auto()
            GLOBALLY = auto()
            PREDICATE = auto()

        poll1 = Poll.objects.create(question="question?", pub_date=timezone.now())
        poll2 = Poll.objects.create(question="ignore this", pub_date=timezone.now())

        def assert_disable_history_info(
            mode: DisableHistoryMode, predicate_target: Union[Type[Poll], Poll] = None
        ):
            # Check the stored info
            attr_name = _StoredDisableHistoryInfo.LOCAL_STORAGE_ATTR_NAME
            info = getattr(HistoricalRecords.context, attr_name, None)
            if mode is DisableHistoryMode.NOT_DISABLED:
                self.assertIsNone(info)
            elif mode is DisableHistoryMode.GLOBALLY:
                self.assertEqual(
                    info, _StoredDisableHistoryInfo(instance_predicate=None)
                )
            elif mode is DisableHistoryMode.PREDICATE:
                self.assertEqual(
                    info, _StoredDisableHistoryInfo(instance_predicate=ANY)
                )
                self.assertIsInstance(info.instance_predicate, Callable)

            # Check `DisableHistoryInfo`
            info = DisableHistoryInfo.get()
            self.assertEqual(info.not_disabled, mode == DisableHistoryMode.NOT_DISABLED)
            self.assertEqual(
                info.disabled_globally, mode == DisableHistoryMode.GLOBALLY
            )
            self.assertEqual(
                info.disabled_for(poll1),
                predicate_target is Poll or predicate_target == poll1,
            )
            self.assertEqual(
                info.disabled_for(poll2),
                predicate_target is Poll or predicate_target == poll2,
            )

            # Check `is_history_disabled()`
            self.assertEqual(is_history_disabled(), mode == DisableHistoryMode.GLOBALLY)
            self.assertEqual(
                is_history_disabled(poll1),
                mode == DisableHistoryMode.GLOBALLY
                or predicate_target is Poll
                or predicate_target == poll1,
            )
            self.assertEqual(
                is_history_disabled(poll2),
                mode == DisableHistoryMode.GLOBALLY
                or predicate_target is Poll
                or predicate_target == poll2,
            )

        assert_disable_history_info(DisableHistoryMode.NOT_DISABLED)

        with disable_history():
            assert_disable_history_info(DisableHistoryMode.GLOBALLY)

        assert_disable_history_info(DisableHistoryMode.NOT_DISABLED)

        with disable_history(only_for_model=Poll):
            assert_disable_history_info(DisableHistoryMode.PREDICATE, Poll)

        assert_disable_history_info(DisableHistoryMode.NOT_DISABLED)

        with disable_history(instance_predicate=lambda poll: "ignore" in poll.question):
            assert_disable_history_info(DisableHistoryMode.PREDICATE, poll2)

        assert_disable_history_info(DisableHistoryMode.NOT_DISABLED)

    @staticmethod
    def _test_disable_poll_history(**kwargs):
        """Create, update and delete some ``Poll`` instances outside and inside
        the context manager."""
        last_pk = 0

        def manipulate_poll(
            poll: Poll = None, *, create=False, update=False, delete=False
        ) -> Poll:
            if create:
                nonlocal last_pk
                last_pk += 1
                poll = Poll.objects.create(
                    pk=last_pk, question=f"qUESTION {last_pk}?", pub_date=timezone.now()
                )
            if update:
                poll.question = f"Question {poll.pk}!"
                poll.save()
            if delete:
                poll.delete()
            return poll

        poll1 = manipulate_poll(create=True, update=True, delete=True)  # noqa: F841
        poll2 = manipulate_poll(create=True, update=True)
        poll3 = manipulate_poll(create=True)

        with disable_history(**kwargs):
            manipulate_poll(poll2, delete=True)
            manipulate_poll(poll3, update=True)
            poll4 = manipulate_poll(create=True, update=True, delete=True)  # noqa: F841
            poll5 = manipulate_poll(create=True, update=True)
            poll6 = manipulate_poll(create=True)

        manipulate_poll(poll5, delete=True)
        manipulate_poll(poll6, update=True)
        poll7 = manipulate_poll(create=True, update=True, delete=True)  # noqa: F841

    expected_poll_records_before_disable: Final = [
        {"id": 1, "question": "qUESTION 1?", "history_type": "+"},
        {"id": 1, "question": "Question 1!", "history_type": "~"},
        {"id": 1, "question": "Question 1!", "history_type": "-"},
        {"id": 2, "question": "qUESTION 2?", "history_type": "+"},
        {"id": 2, "question": "Question 2!", "history_type": "~"},
        {"id": 3, "question": "qUESTION 3?", "history_type": "+"},
    ]
    expected_poll_records_during_disable: Final = [
        {"id": 2, "question": "Question 2!", "history_type": "-"},
        {"id": 3, "question": "Question 3!", "history_type": "~"},
        {"id": 4, "question": "qUESTION 4?", "history_type": "+"},
        {"id": 4, "question": "Question 4!", "history_type": "~"},
        {"id": 4, "question": "Question 4!", "history_type": "-"},
        {"id": 5, "question": "qUESTION 5?", "history_type": "+"},
        {"id": 5, "question": "Question 5!", "history_type": "~"},
        {"id": 6, "question": "qUESTION 6?", "history_type": "+"},
    ]
    expected_poll_records_after_disable: Final = [
        {"id": 5, "question": "Question 5!", "history_type": "-"},
        {"id": 6, "question": "Question 6!", "history_type": "~"},
        {"id": 7, "question": "qUESTION 7?", "history_type": "+"},
        {"id": 7, "question": "Question 7!", "history_type": "~"},
        {"id": 7, "question": "Question 7!", "history_type": "-"},
    ]

    @staticmethod
    def _test_disable_poll_with_m2m_history(**kwargs):
        """Create some ``PollWithManyToMany`` instances and add, remove, set and clear
        their ``Place`` relations outside and inside the context manager."""
        last_pk = 0
        place1 = Place.objects.create(pk=1, name="1")
        place2 = Place.objects.create(pk=2, name="2")

        def manipulate_places(
            poll=None, *, add=False, remove=False, set=False, clear=False
        ) -> PollWithManyToMany:
            if not poll:
                nonlocal last_pk
                last_pk += 1
                poll = PollWithManyToMany.objects.create(
                    pk=last_pk, question=f"{last_pk}?", pub_date=timezone.now()
                )
            if add:
                poll.places.add(place1)
            if remove:
                poll.places.remove(place1)
            if set:
                poll.places.set([place2])
            if clear:
                poll.places.clear()
            return poll

        poll1 = manipulate_places(  # noqa: F841
            add=True, remove=True, set=True, clear=True
        )
        poll2 = manipulate_places(add=True, remove=True, set=True)
        poll3 = manipulate_places(add=True, remove=True)
        poll4 = manipulate_places(add=True)

        with disable_history(**kwargs):
            manipulate_places(poll2, clear=True)
            manipulate_places(poll3, set=True, clear=True)
            manipulate_places(poll4, remove=True, set=True, clear=True)
            poll5 = manipulate_places(  # noqa: F841
                add=True, remove=True, set=True, clear=True
            )
            poll6 = manipulate_places(add=True, remove=True, set=True)
            poll7 = manipulate_places(add=True, remove=True)
            poll8 = manipulate_places(add=True)

        manipulate_places(poll6, clear=True)
        manipulate_places(poll7, set=True, clear=True)
        manipulate_places(poll8, remove=True, set=True, clear=True)
        poll9 = manipulate_places(  # noqa: F841
            add=True, remove=True, set=True, clear=True
        )

    expected_poll_with_m2m_records_before_disable: Final = [
        {"id": 1, "question": "1?", "history_type": "+", "places": []},
        {"id": 1, "question": "1?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 1, "question": "1?", "history_type": "~", "places": []},
        {"id": 1, "question": "1?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 1, "question": "1?", "history_type": "~", "places": []},
        {"id": 2, "question": "2?", "history_type": "+", "places": []},
        {"id": 2, "question": "2?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 2, "question": "2?", "history_type": "~", "places": []},
        {"id": 2, "question": "2?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 3, "question": "3?", "history_type": "+", "places": []},
        {"id": 3, "question": "3?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 3, "question": "3?", "history_type": "~", "places": []},
        {"id": 4, "question": "4?", "history_type": "+", "places": []},
        {"id": 4, "question": "4?", "history_type": "~", "places": [Place(pk=1)]},
    ]
    expected_poll_with_m2m_records_during_disable: Final = [
        {"id": 2, "question": "2?", "history_type": "~", "places": []},
        {"id": 3, "question": "3?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 3, "question": "3?", "history_type": "~", "places": []},
        {"id": 4, "question": "4?", "history_type": "~", "places": []},
        {"id": 4, "question": "4?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 4, "question": "4?", "history_type": "~", "places": []},
        {"id": 5, "question": "5?", "history_type": "+", "places": []},
        {"id": 5, "question": "5?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 5, "question": "5?", "history_type": "~", "places": []},
        {"id": 5, "question": "5?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 5, "question": "5?", "history_type": "~", "places": []},
        {"id": 6, "question": "6?", "history_type": "+", "places": []},
        {"id": 6, "question": "6?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 6, "question": "6?", "history_type": "~", "places": []},
        {"id": 6, "question": "6?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 7, "question": "7?", "history_type": "+", "places": []},
        {"id": 7, "question": "7?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 7, "question": "7?", "history_type": "~", "places": []},
        {"id": 8, "question": "8?", "history_type": "+", "places": []},
        {"id": 8, "question": "8?", "history_type": "~", "places": [Place(pk=1)]},
    ]
    expected_poll_with_m2m_records_after_disable: Final = [
        {"id": 6, "question": "6?", "history_type": "~", "places": []},
        {"id": 7, "question": "7?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 7, "question": "7?", "history_type": "~", "places": []},
        {"id": 8, "question": "8?", "history_type": "~", "places": []},
        {"id": 8, "question": "8?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 8, "question": "8?", "history_type": "~", "places": []},
        {"id": 9, "question": "9?", "history_type": "+", "places": []},
        {"id": 9, "question": "9?", "history_type": "~", "places": [Place(pk=1)]},
        {"id": 9, "question": "9?", "history_type": "~", "places": []},
        {"id": 9, "question": "9?", "history_type": "~", "places": [Place(pk=2)]},
        {"id": 9, "question": "9?", "history_type": "~", "places": []},
    ]

    def test__disable_history__with_no_args(self):
        """Test that no historical records are created inside the context manager with
        no arguments (i.e. history is globally disabled)."""
        # Test with `Poll` instances
        self._test_disable_poll_history()
        expected_records = [
            *self.expected_poll_records_before_disable,
            *self.expected_poll_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

        # Test with `PollWithManyToMany` instances
        self._test_disable_poll_with_m2m_history()
        expected_records = [
            *self.expected_poll_with_m2m_records_before_disable,
            *self.expected_poll_with_m2m_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(PollWithManyToMany, expected_records)

    def test__disable_history__with__only_for_model__poll(self):
        """Test that no historical records are created for ``Poll`` instances inside
        the context manager with ``only_for_model=Poll`` as argument."""
        # Test with `Poll` instances
        self._test_disable_poll_history(only_for_model=Poll)
        expected_records = [
            *self.expected_poll_records_before_disable,
            *self.expected_poll_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

        # Test with `PollWithManyToMany` instances
        self._test_disable_poll_with_m2m_history(only_for_model=Poll)
        expected_records = [
            *self.expected_poll_with_m2m_records_before_disable,
            *self.expected_poll_with_m2m_records_during_disable,
            *self.expected_poll_with_m2m_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(PollWithManyToMany, expected_records)

    def test__disable_history__with__only_for_model__poll_with_m2m(self):
        """Test that no historical records are created for ``PollWithManyToMany``
        instances inside the context manager with ``only_for_model=PollWithManyToMany``
        as argument."""
        # Test with `Poll` instances
        self._test_disable_poll_history(only_for_model=PollWithManyToMany)
        expected_records = [
            *self.expected_poll_records_before_disable,
            *self.expected_poll_records_during_disable,
            *self.expected_poll_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

        # Test with `PollWithManyToMany` instances
        self._test_disable_poll_with_m2m_history(only_for_model=PollWithManyToMany)
        expected_records = [
            *self.expected_poll_with_m2m_records_before_disable,
            *self.expected_poll_with_m2m_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(PollWithManyToMany, expected_records)

    def test__disable_history__with__instance_predicate(self):
        """Test that no historical records are created inside the context manager, for
        model instances that match the provided ``instance_predicate`` argument."""
        # Test with `Poll` instances
        self._test_disable_poll_history(instance_predicate=lambda poll: poll.pk == 4)
        expected_records = [
            *self.expected_poll_records_before_disable,
            *filter(
                lambda poll_dict: poll_dict["id"] != 4,
                self.expected_poll_records_during_disable,
            ),
            *self.expected_poll_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

        # Test with `PollWithManyToMany` instances
        self._test_disable_poll_with_m2m_history(
            instance_predicate=lambda poll: poll.pk == 5
        )
        expected_records = [
            *self.expected_poll_with_m2m_records_before_disable,
            *filter(
                lambda poll_dict: poll_dict["id"] != 5,
                self.expected_poll_with_m2m_records_during_disable,
            ),
            *self.expected_poll_with_m2m_records_after_disable,
        ]
        self.assert_all_records_of_model_equal(PollWithManyToMany, expected_records)

    def test__disable_history__for_queryset_delete(self):
        """Test that no historical records are created inside the context manager when
        deleting objects using the ``delete()`` queryset method."""
        Poll.objects.create(pk=1, question="delete me", pub_date=timezone.now())
        Poll.objects.create(pk=2, question="keep me", pub_date=timezone.now())
        Poll.objects.create(pk=3, question="keep me", pub_date=timezone.now())
        Poll.objects.create(pk=4, question="delete me", pub_date=timezone.now())

        with disable_history():
            Poll.objects.filter(question__startswith="delete").delete()

        expected_records = [
            {"id": 1, "question": "delete me", "history_type": "+"},
            {"id": 2, "question": "keep me", "history_type": "+"},
            {"id": 3, "question": "keep me", "history_type": "+"},
            {"id": 4, "question": "delete me", "history_type": "+"},
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

        Poll.objects.all().delete()
        expected_records += [
            # Django reverses the order before sending the `post_delete` signals
            # while bulk-deleting
            {"id": 3, "question": "keep me", "history_type": "-"},
            {"id": 2, "question": "keep me", "history_type": "-"},
        ]
        self.assert_all_records_of_model_equal(Poll, expected_records)

    def test__disable_history__for_foreign_key_cascade_delete(self):
        """Test that no historical records are created inside the context manager when
        indirectly deleting objects through a foreign key relationship with
        ``on_delete=CASCADE``."""
        poll1 = Poll.objects.create(pk=1, pub_date=timezone.now())
        poll2 = Poll.objects.create(pk=2, pub_date=timezone.now())
        Choice.objects.create(pk=11, poll=poll1, votes=0)
        Choice.objects.create(pk=12, poll=poll1, votes=0)
        Choice.objects.create(pk=21, poll=poll2, votes=0)
        Choice.objects.create(pk=22, poll=poll2, votes=0)

        with disable_history():
            poll1.delete()

        expected_records = [
            {"id": 11, "poll_id": 1, "history_type": "+"},
            {"id": 12, "poll_id": 1, "history_type": "+"},
            {"id": 21, "poll_id": 2, "history_type": "+"},
            {"id": 22, "poll_id": 2, "history_type": "+"},
        ]
        self.assert_all_records_of_model_equal(Choice, expected_records)

        poll2.delete()
        expected_records += [
            # Django reverses the order before sending the `post_delete` signals
            # while bulk-deleting
            {"id": 22, "poll_id": 2, "history_type": "-"},
            {"id": 21, "poll_id": 2, "history_type": "-"},
        ]
        self.assert_all_records_of_model_equal(Choice, expected_records)

    def assert_all_records_of_model_equal(
        self, model: Type[Model], expected_records: List[dict]
    ):
        records = model.history.all()
        self.assertEqual(len(records), len(expected_records))
        for record, expected_record in zip(reversed(records), expected_records):
            with self.subTest(record=record, expected_record=expected_record):
                self.assertRecordValues(record, model, expected_record)

    def test_providing_illegal_arguments_fails(self):
        """Test that providing various illegal arguments and argument combinations
        fails."""

        def predicate(_):
            return True

        # Providing both arguments should fail
        with self.assertRaises(ValueError):
            with disable_history(only_for_model=Poll, instance_predicate=predicate):
                pass
        # Providing the arguments individually should not fail
        with disable_history(only_for_model=Poll):
            pass
        with disable_history(instance_predicate=predicate):
            pass

        # Passing non-history-tracked models should fail
        with self.assertRaises(NotHistoricalModelError):
            with disable_history(only_for_model=Place):
                pass
        # Passing non-history-tracked model instances should fail
        place = Place.objects.create()
        with self.assertRaises(NotHistoricalModelError):
            is_history_disabled(place)

    def test_nesting_fails(self):
        """Test that nesting ``disable_history()`` contexts fails."""
        # Nesting (twice or more) should fail
        with self.assertRaises(AssertionError):
            with disable_history():
                with disable_history():
                    pass
        with self.assertRaises(AssertionError):
            with disable_history():
                with disable_history():
                    with disable_history():
                        pass
        # No nesting should not fail
        with disable_history():
            pass


class UpdateChangeReasonTestCase(TestCase):
    def test_update_change_reason_with_excluded_fields(self):
        poll = PollWithExcludeFields(
            question="what's up?", pub_date=timezone.now(), place="The Pub"
        )
        poll.save()
        update_change_reason(poll, "Test change reason.")
        most_recent = poll.history.order_by("-history_date").first()
        self.assertEqual(most_recent.history_change_reason, "Test change reason.")


@dataclass
class HistoryTrackedModelTestInfo:
    model: Type[Model]
    history_manager_name: Optional[str]
    init_kwargs: dict

    def __init__(
        self,
        model: Type[Model],
        history_manager_name: Optional[str] = "history",
        **init_kwargs,
    ):
        self.model = model
        self.history_manager_name = history_manager_name
        self.init_kwargs = init_kwargs


class GetHistoryManagerAndModelHelpersTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user = User.objects.create(username="user")
        poll_kwargs = {"pub_date": timezone.now()}
        poll = Poll.objects.create(**poll_kwargs)
        choice_kwargs = {"poll": poll, "votes": 0}
        choice = Choice.objects.create(**choice_kwargs)
        place = Place.objects.create()
        org_kwarg = {
            "organization": TestOrganizationWithHistory.objects.create(),
        }

        H = HistoryTrackedModelTestInfo
        cls.history_tracked_models = [
            H(Choice, **choice_kwargs),
            H(ConcreteAttr),
            H(ConcreteExternal),
            H(ConcreteUtil),
            H(Contact),
            H(ContactRegister),
            H(CustomManagerNameModel, "log"),
            H(ExternalModelSpecifiedWithAppParam, "histories"),
            H(ExternalModelWithAppLabel),
            H(InheritTracking1),
            H(ModelWithHistoryInDifferentApp),
            H(ModelWithHistoryUsingBaseModelDb),
            H(OverrideModelNameAsCallable),
            H(OverrideModelNameRegisterMethod1),
            H(OverrideModelNameUsingBaseModel1),
            H(Poll, **poll_kwargs),
            H(PollChildBookWithManyToMany, **poll_kwargs),
            H(PollWithAlternativeManager, **poll_kwargs),
            H(PollWithCustomManager, **poll_kwargs),
            H(PollWithExcludedFKField, place=place, **poll_kwargs),
            H(PollWithHistoricalSessionAttr),
            H(PollWithManyToMany, **poll_kwargs),
            H(PollWithManyToManyCustomHistoryID, **poll_kwargs),
            H(PollWithManyToManyWithIPAddress, **poll_kwargs),
            H(PollWithQuerySetCustomizations, **poll_kwargs),
            H(PollWithSelfManyToMany),
            H(Restaurant, "updates", rating=0),
            H(TestHistoricParticipanToHistoricOrganization, **org_kwarg),
            H(TrackedConcreteBase),
            H(TrackedWithAbstractBase),
            H(TrackedWithConcreteBase),
            H(Voter, user=user, choice=choice),
            H(external.ExternalModel),
            H(external.ExternalModelRegistered, "histories"),
            H(external.Poll),
        ]
        cls.models_without_history_manager = [
            H(AbstractBase, None),
            H(AbstractModelCallable1, None),
            H(BaseModel, None),
            H(FirstLevelInheritedModel, None),
            H(HardbackBook, None, isbn="123", price=0),
            H(Place, None),
            H(PollParentWithManyToMany, None, **poll_kwargs),
            H(Profile, None, date_of_birth=timezone.now().date()),
            H(TestParticipantToHistoricOrganization, None, **org_kwarg),
            H(TrackedAbstractBaseA, None),
        ]

    def test__get_history_manager_for_model(self):
        """Test that ``get_history_manager_for_model()`` returns the expected value
        for various models."""

        def assert_history_manager(history_manager, info: HistoryTrackedModelTestInfo):
            expected_manager = getattr(info.model, info.history_manager_name)
            expected_historical_model = expected_manager.model
            historical_model = history_manager.model
            # Can't compare the managers directly, as the history manager classes are
            # dynamically created through `HistoryDescriptor`
            self.assertIsInstance(history_manager, HistoryManager)
            self.assertIsInstance(expected_manager, HistoryManager)
            self.assertTrue(issubclass(historical_model, HistoricalChanges))
            self.assertEqual(historical_model.instance_type, info.model)
            self.assertEqual(historical_model, expected_historical_model)

        for model_info in self.history_tracked_models:
            with self.subTest(model_info=model_info):
                model = model_info.model
                manager = get_history_manager_for_model(model)
                assert_history_manager(manager, model_info)

                # Passing a model instance should also work
                instance = model(**model_info.init_kwargs)
                instance.save()
                manager = get_history_manager_for_model(instance)
                assert_history_manager(manager, model_info)

        for model_info in self.models_without_history_manager:
            with self.subTest(model_info=model_info):
                model = model_info.model
                with self.assertRaises(NotHistoricalModelError):
                    get_history_manager_for_model(model)

                # The same error should be raised if passing a model instance
                if not model._meta.abstract:
                    instance = model(**model_info.init_kwargs)
                    instance.save()
                    with self.assertRaises(NotHistoricalModelError):
                        get_history_manager_for_model(instance)

    def test__get_history_model_for_model(self):
        """Test that ``get_history_model_for_model()`` returns the expected value
        for various models."""
        for model_info in self.history_tracked_models:
            with self.subTest(model_info=model_info):
                model = model_info.model
                historical_model = get_history_model_for_model(model)
                self.assertTrue(issubclass(historical_model, HistoricalChanges))
                self.assertEqual(historical_model.instance_type, model)

                # Passing a model instance should also work
                instance = model(**model_info.init_kwargs)
                instance.save()
                historical_model_from_instance = get_history_model_for_model(instance)
                self.assertEqual(historical_model_from_instance, historical_model)

        for model_info in self.models_without_history_manager:
            with self.subTest(model_info=model_info):
                model = model_info.model
                with self.assertRaises(NotHistoricalModelError):
                    get_history_model_for_model(model)

                # The same error should be raised if passing a model instance
                if not model._meta.abstract:
                    instance = model(**model_info.init_kwargs)
                    instance.save()
                    with self.assertRaises(NotHistoricalModelError):
                        get_history_model_for_model(instance)

    def test__get_pk_name(self):
        """Test that ``get_pk_name()`` returns the expected value for various models."""
        self.assertEqual(get_pk_name(Poll), "id")
        self.assertEqual(get_pk_name(PollInfo), "poll_id")
        self.assertEqual(get_pk_name(Book), "isbn")

        self.assertEqual(get_pk_name(HistoricalPoll), "history_id")
        self.assertEqual(get_pk_name(HistoricalPollInfo), "history_id")
        self.assertEqual(get_pk_name(HistoricalBook), "history_id")


class GetHistoricalRecordsOfInstanceTestCase(TestCase):
    def test__get_historical_records_of_instance(self):
        """Test that ``get_historical_records_of_instance()`` returns the expected
        queryset for history-tracked model instances."""
        poll1 = Poll.objects.create(pub_date=timezone.now())
        poll1_history = poll1.history.all()
        (record1_1,) = poll1_history
        self.assertQuerySetEqual(
            get_historical_records_of_instance(record1_1),
            poll1_history,
        )

        poll2 = Poll.objects.create(pub_date=timezone.now())
        poll2.question = "?"
        poll2.save()
        poll2_history = poll2.history.all()
        (record2_2, record2_1) = poll2_history
        self.assertQuerySetEqual(
            get_historical_records_of_instance(record2_1),
            poll2_history,
        )
        self.assertQuerySetEqual(
            get_historical_records_of_instance(record2_2),
            poll2_history,
        )

        poll3 = Poll.objects.create(id=123, pub_date=timezone.now())
        poll3.delete()
        poll3_history = Poll.history.filter(id=123)
        (record3_2, record3_1) = poll3_history
        self.assertQuerySetEqual(
            get_historical_records_of_instance(record3_1),
            poll3_history,
        )
        self.assertQuerySetEqual(
            get_historical_records_of_instance(record3_2),
            poll3_history,
        )


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
    def test_bulk_create_history_without_history_enabled(self):
        with self.assertNumQueries(1):
            bulk_create_with_history(self.data, Poll)

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.history.count(), 0)

    def test_bulk_create_history_with__disable_history(self):
        with self.assertNumQueries(1):
            with disable_history(only_for_model=Poll):
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
        # 5 records from `setUp()`
        self.assertEqual(Poll.history.count(), 5)
        bulk_update_with_history(self.data, Poll, fields=["question"])

        self.assertEqual(Poll.objects.count(), 5)
        self.assertEqual(Poll.objects.get(id=4).question, "Updated question")
        self.assertEqual(Poll.history.count(), 5)
        self.assertEqual(Poll.history.filter(history_type="~").count(), 0)

    def test_bulk_update_history_with__disable_history(self):
        # 5 records from `setUp()`
        self.assertEqual(Poll.history.count(), 5)
        with disable_history(only_for_model=Poll):
            bulk_update_with_history(self.data, Poll, fields=["question"])

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
