import unittest


class DeprecationWarningTest(unittest.TestCase):
    """Tests that check whether ``DeprecationWarning`` is raised for certain features,
    and that compare ``simple_history.__version__`` against the version the features
    will be removed in.

    If this class is empty, it normally means that nothing is currently deprecated.
    """
