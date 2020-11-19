from datetime import datetime

from django.test import TestCase

from simple_history.signals import (
    post_create_historical_record,
    pre_create_historical_record,
)

from ..models import Poll

today = datetime(2021, 1, 1, 10, 0)


class PrePostCreateHistoricalRecordSignalTest(TestCase):
    def setUp(self):
        self.signal_was_called = False
        self.signal_instance = None
        self.signal_history_instance = None
        self.signal_sender = None

    def test_pre_create_historical_record_signal(self):
        def handler(sender, instance, **kwargs):
            self.signal_was_called = True
            self.signal_instance = instance
            self.signal_history_instance = kwargs["history_instance"]
            self.signal_sender = sender

        pre_create_historical_record.connect(handler)

        p = Poll(question="what's up?", pub_date=today)
        p.save()

        self.assertTrue(self.signal_was_called)
        self.assertEqual(self.signal_instance, p)
        self.assertIsNotNone(self.signal_history_instance)
        self.assertEqual(self.signal_sender, p.history.first().__class__)

    def test_post_create_historical_record_signal(self):
        def handler(sender, instance, history_instance, **kwargs):
            self.signal_was_called = True
            self.signal_instance = instance
            self.signal_history_instance = history_instance
            self.signal_sender = sender

        post_create_historical_record.connect(handler)

        p = Poll(question="what's up?", pub_date=today)
        p.save()

        self.assertTrue(self.signal_was_called)
        self.assertEqual(self.signal_instance, p)
        self.assertIsNotNone(self.signal_history_instance)
        self.assertEqual(self.signal_sender, p.history.first().__class__)
