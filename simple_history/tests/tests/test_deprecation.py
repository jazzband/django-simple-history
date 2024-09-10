from django.test import TestCase
from django.utils import timezone

from simple_history import __version__
from simple_history.models import HistoricalRecords
from simple_history.templatetags.simple_history_admin_list import display_list

from ..models import Place, PollWithManyToMany


class DeprecationWarningTest(TestCase):
    def test__display_list__warns_deprecation(self):
        with self.assertWarns(DeprecationWarning):
            display_list({})
        # DEV: `display_list()` (and the file `simple_history_admin_list.py`) should be
        #      removed when 3.8 is released
        self.assertLess(__version__, "3.8")

    def test__HistoricalRecords_thread__warns_deprecation(self):
        with self.assertWarns(DeprecationWarning):
            context = HistoricalRecords.thread
            self.assertIs(context, HistoricalRecords.context)
        with self.assertWarns(DeprecationWarning):
            context = getattr(HistoricalRecords, "thread")
            self.assertIs(context, HistoricalRecords.context)
        with self.assertWarns(DeprecationWarning):
            context = HistoricalRecords().thread
            self.assertIs(context, HistoricalRecords.context)
        with self.assertWarns(DeprecationWarning):
            context = getattr(HistoricalRecords(), "thread")
            self.assertIs(context, HistoricalRecords.context)

        # DEV: `_DeprecatedThreadDescriptor` and the `thread` attribute of
        #      `HistoricalRecords` should be removed when 3.10 is released
        self.assertLess(__version__, "3.10")

    def test__skip_history_when_saving__warns_deprecation(self):
        place = Place.objects.create(name="Here")

        poll = PollWithManyToMany(question="why?", pub_date=timezone.now())
        poll.skip_history_when_saving = True
        with self.assertWarns(DeprecationWarning):
            poll.save()
        poll.question = "how?"
        with self.assertWarns(DeprecationWarning):
            poll.save()
        with self.assertWarns(DeprecationWarning):
            poll.places.add(place)
        self.assertEqual(PollWithManyToMany.history.count(), 0)
        self.assertEqual(poll.history.count(), 0)

        # DEV: The `if` statements checking for `skip_history_when_saving` (in the
        #      `post_save()` and `m2m_changed()` methods of `HistoricalRecords`)
        #      should be removed when 4.0 is released
        self.assertLess(__version__, "4.0")
