import unittest

from simple_history import __version__
from simple_history.templatetags.simple_history_admin_list import display_list


class DeprecationWarningTest(unittest.TestCase):
    def test__display_list__warns_deprecation_and_is_yet_to_be_removed(self):
        with self.assertWarns(DeprecationWarning):
            display_list({})
        # DEV: `display_list()` (and the file `simple_history_admin_list.py`) should be
        #      removed when 3.8 is released
        self.assertLess(__version__, "3.8")
