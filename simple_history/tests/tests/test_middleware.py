from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse

from simple_history.tests.custom_user.models import CustomUser
from simple_history.tests.models import (
    BucketDataRegisterRequestUser,
    BucketMember,
    Poll
)
from simple_history.tests.tests.utils import middleware_override_settings


@override_settings(**middleware_override_settings)
class MiddlewareTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(
            'user_login',
            'u@example.com',
            'pass'
        )

    def test_user_is_set_on_create_view_when_logged_in(self):
        self.client.force_login(self.user)
        data = {
            'question': 'Test question',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-add'), data=data)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [self.user.id])

    def test_user_is_not_set_on_create_view_not_logged_in(self):
        data = {
            'question': 'Test question',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-add'), data=data)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [None])

    def test_user_is_set_on_update_view_when_logged_in(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(
            question='Test question',
            pub_date=date.today()
        )
        data = {
            'question': 'Test question updated',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-update', args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, 'Test question updated')

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [self.user.id, None])

    def test_user_is_not_set_on_update_view_when_not_logged_in(self):
        poll = Poll.objects.create(
            question='Test question',
            pub_date=date.today()
        )
        data = {
            'question': 'Test question updated',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-update', args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, 'Test question updated')

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [None, None])

    def test_user_is_unset_on_update_view_after_logging_out(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(
            question='Test question',
            pub_date=date.today()
        )
        data = {
            'question': 'Test question updated',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-update', args=[poll.pk]), data=data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, 'Test question updated')

        self.client.logout()

        new_data = {
            'question': 'Test question updated part 2',
            'pub_date': '2010-01-01'
        }
        self.client.post(reverse('poll-update', args=[poll.pk]), data=new_data)

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll = polls.first()
        self.assertEqual(poll.question, 'Test question updated part 2')

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [None, self.user.id, None])

    def test_user_is_set_on_delete_view_when_logged_in(self):
        self.client.force_login(self.user)
        poll = Poll.objects.create(
            question='Test question',
            pub_date=date.today()
        )

        self.client.post(reverse('poll-delete', args=[poll.pk]))

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 0)

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [self.user.id, None])

    def test_user_is_not_set_on_delete_view_when_not_logged_in(self):
        poll = Poll.objects.create(
            question='Test question',
            pub_date=date.today()
        )

        self.client.post(reverse('poll-delete', args=[poll.pk]))

        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 0)

        poll_history = poll.history.all()

        self.assertListEqual([ph.history_user_id for ph in poll_history],
                             [None, None])

    def test_bucket_member_is_set_on_create_view_when_logged_in(self):
        self.client.force_login(self.user)
        member1 = BucketMember.objects.create(name="member1", user=self.user)
        data = {
            'data': 'Test Data',
        }
        self.client.post(reverse('bucket_data-add'), data=data)
        bucket_datas = BucketDataRegisterRequestUser.objects.all()
        self.assertEqual(bucket_datas.count(), 1)

        history = bucket_datas.first().history.all()

        self.assertListEqual([h.history_user_id for h in history],
                             [member1.id])

    def test_remote_addr_is_set_when_x_forwarded_for_is_available(self):
        data = {
            'question': 'Test question',
            'pub_date': '2010-01-01'
        }
        headers = {'HTTP_X_FORWARDED_FOR': '1.2.3.4'}
        self.client.post(reverse('poll-add'), data=data, **headers)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual([ph.history_remote_addr for ph in poll_history],
                             ['1.2.3.4'])

    def test_remote_addr_fallback_when_not_using_reverse_proxy(self):
        """
        Test fallback to REMOTE_ADDR header when HTTP_X_FORWARDED_FOR
        is not available.
        """
        data = {
            'question': 'Test question',
            'pub_date': '2010-01-01'
        }
        headers = {
            'HTTP_X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '4.3.2.1'
        }
        self.client.post(reverse('poll-add'), data=data, **headers)
        polls = Poll.objects.all()
        self.assertEqual(polls.count(), 1)

        poll_history = polls.first().history.all()

        self.assertListEqual([ph.history_remote_addr for ph in poll_history],
                             ['4.3.2.1'])
