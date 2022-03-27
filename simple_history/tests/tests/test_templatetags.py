from django.test import TestCase

from simple_history.templatetags.getattributes import getattribute


class Foo:
    bar = "bar"


class TestGetAttributes(TestCase):
    def test_get_existing_attributes_return_it(self):
        self.assertEqual(getattribute(Foo(), "bar"), "bar")

    def test_get_missing_attributes_return_None(self):
        self.assertIsNone(getattribute(Foo(), "baz"))
