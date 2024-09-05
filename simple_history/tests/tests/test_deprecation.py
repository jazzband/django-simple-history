import unittest

from simple_history import __version__
from simple_history.models import HistoricalRecords
from simple_history.templatetags.simple_history_admin_list import display_list


class DeprecationWarningTest(unittest.TestCase):
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
