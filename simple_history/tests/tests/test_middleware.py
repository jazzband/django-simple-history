from datetime import date
from unittest import mock

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse

from simple_history.models import HistoricalRecords
from simple_history.tests.custom_user.models import CustomUser
from simple_history.tests.models import (
    BucketDataRegisterRequestUser,
    BucketMember,
    Poll,
)
from simple_history.tests.tests.utils import middleware_override_settings


@override_settings(**middleware_override_settings)
class MiddlewareTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(
            "user_login", "u@example.com", "pass"
        )

    def test_user_is_set_on_create_view_when_logged_in(self):
        self.client.force_login(self.user)
        data = {"question": "Test question", "pub_date": "2010-01-01"}
        self.client.post(reverse("poll-add"), data=data)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual(
            [ph.history_user_id for ph in poll_history], [self.user.id]
        )

    def test_user_is_not_set_on_create_view_not_logged_in(self):
        data = {"question": "Test question", "pub_date": "2010-01-01"}
        self.client.post(reverse("poll-add"), data=data)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history], [None])

    def test_user_is_set_on_update_view_when_logged_in(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(question="Test question", pub_date=date.today())
        data = {"question": "Test question updated", "pub_date": "2010-01-01"}
        self.client.post(reverse("poll-update", args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, "Test question updated")

        poll_history = poll.history.all()

        self.assertListEqual(
            [ph.history_user_id for ph in poll_history], [self.user.id, None]
        )

    def test_user_is_not_set_on_update_view_when_not_logged_in(self):
        poll = Poll.objects.create(question="Test question", pub_date=date.today())
        data = {"question": "Test question updated", "pub_date": "2010-01-01"}
        self.client.post(reverse("poll-update", args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, "Test question updated")

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history], [None, None])

    def test_user_is_unset_on_update_view_after_logging_out(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(question="Test question", pub_date=date.today())
        data = {"question": "Test question updated", "pub_date": "2010-01-01"}
        self.client.post(reverse("poll-update", args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, "Test question updated")

        self.client.logout()

        new_data = {
            "question": "Test question updated part 2",
            "pub_date": "2010-01-01",
        }
        self.client.post(reverse("poll-update", args=[poll.pk]), data=new_data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, "Test question updated part 2")

        poll_history = poll.history.all()

        self.assertListEqual(
            [ph.history_user_id for ph in poll_history], [None, self.user.id, None]
        )

    def test_user_is_set_on_delete_view_when_logged_in(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(question="Test question", pub_date=date.today())

        self.client.post(reverse("poll-delete", args=[poll.pk]))

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 0)

        poll_history = poll.history.all()

        self.assertListEqual(
            [ph.history_user_id for ph in poll_history], [self.user.id, None]
        )

    def test_user_is_not_set_on_delete_view_when_not_logged_in(self):
        poll = Poll.objects.create(question="Test question", pub_date=date.today())

        self.client.post(reverse("poll-delete", args=[poll.pk]))

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 0)

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history], [None, None])

    def test_bucket_member_is_set_on_create_view_when_logged_in(self):
        self.client.force_login(self.user)
        member1 = BucketMember.objects.create(name="member1", user=self.user)
        data = {"data": "Test Data"}
        self.client.post(reverse("bucket_data-add"), data=data)
        bucket_datas = BucketDataRegisterRequestUser.objects.all()
        self.assertEqual(bucket_datas.count(), 1)

        history = bucket_datas.first().history.all()

        self.assertListEqual([h.history_user_id for h in history], [member1.id])

    # The `request` attribute of `HistoricalRecords.context` should be deleted
    # even if this setting is set to `True`
    @override_settings(DEBUG_PROPAGATE_EXCEPTIONS=True)
    @mock.patch("simple_history.tests.view.MockableView.get")
    def test_request_attr_is_deleted_after_each_response(self, func_mock):
        """https://github.com/django-commons/django-simple-history/issues/1189"""

        def assert_has_request_attr(has_attr: bool):
            self.assertEqual(hasattr(HistoricalRecords.context, "request"), has_attr)

        def mocked_get(*args, **kwargs):
            assert_has_request_attr(True)
            response_ = HttpResponse(status=200)
            response_.historical_records_request = HistoricalRecords.context.request
            return response_

        func_mock.side_effect = mocked_get
        self.client.force_login(self.user)
        mockable_url = reverse("mockable")

        assert_has_request_attr(False)
        response = self.client.get(mockable_url)
        assert_has_request_attr(False)
        # Check that the `request` attr existed while handling the request
        self.assertEqual(response.historical_records_request.user, self.user)

        func_mock.side_effect = RuntimeError()
        with self.assertRaises(RuntimeError):
            self.client.get(mockable_url)
        # The request variable should be deleted even if an exception was raised
        assert_has_request_attr(False)


@override_settings(**middleware_override_settings)
class MiddlewareBulkOpsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(
            "user_login", "u@example.com", "pass"
        )

    def test_user_is_set_on_bulk_create_view_when_logged_in(self):
        self.client.force_login(self.user)
        self.client.post(reverse("poll-bulk-create"), data={})
        polls = Poll.objects.all()
        self.assertEqual(len(polls), 2)

        poll_history = Poll.history.all()

        self.assertCountEqual(
            [ph.history_user_id for ph in poll_history], [self.user.id, self.user.id]
        )

    def test_user_is_not_set_on_bulk_create_view_not_logged_in(self):
        self.client.post(reverse("poll-bulk-create"), data={})

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 2)

        poll_history = Poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history], [None, None])

    def test_request_user_is_overwritten_by_default_user_on_bulk_create_view(
        self,
    ):
        self.client.force_login(self.user)
        self.client.post(reverse("poll-bulk-create-with-default-user"), data={})

        polls = Poll.objects.all()
        self.assertEqual(len(polls), 2)

        poll_history = Poll.history.all()

        self.assertFalse(any(ph.history_user_id == self.user.id for ph in poll_history))
        self.assertFalse(any(ph.history_user_id is None for ph in poll_history))

    def test_user_is_set_on_bulk_update_view_when_logged_in(self):
        self.client.force_login(self.user)
        poll_1 = Poll.objects.create(question="Test question 1", pub_date=date.today())
        poll_2 = Poll.objects.create(
            question="Test question 2", pub_date=date(2020, 1, 1)
        )

        self.client.post(reverse("poll-bulk-update"), data={})

        polls = Poll.objects.all()
        self.assertEqual(2, len(polls))

        self.assertEqual("1", poll_1.history.latest("history_date").question)
        self.assertEqual("0", poll_2.history.latest("history_date").question)
        self.assertEqual(
            self.user.id, poll_1.history.latest("history_date").history_user_id
        )
        self.assertEqual(
            self.user.id, poll_2.history.latest("history_date").history_user_id
        )

    def test_user_is_not_set_on_bulk_update_view_when_not_logged_in(self):
        poll_1 = Poll.objects.create(question="Test question 1", pub_date=date.today())
        poll_2 = Poll.objects.create(
            question="Test question 2", pub_date=date(2020, 1, 1)
        )

        self.client.post(reverse("poll-bulk-update"), data={})

        self.assertIsNone(poll_1.history.latest("history_date").history_user_id)
        self.assertIsNone(poll_2.history.latest("history_date").history_user_id)

    def test_request_user_is_overwritten_by_default_user_on_bulk_update(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(pub_date=date(2020, 1, 1), question="123")

        self.client.post(reverse("poll-bulk-update-with-default-user"), data={})

        self.assertIsNotNone(poll.history.latest("history_date").history_user_id)
        self.assertNotEqual(
            self.user.id, poll.history.latest("history_date").history_user_id
        )
