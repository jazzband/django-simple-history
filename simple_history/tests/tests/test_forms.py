from django.test import TestCase

from django.forms import ModelForm
import django
from django.utils import six

from ..models import Dummy
from ..forms import ReadOnlyFieldsMixin


class FooModelForm(ReadOnlyFieldsMixin, ModelForm):
    class Meta:
        model = Dummy
        if django.VERSION >= (1, 6):
            fields = '__all__'


class BarModelForm(ReadOnlyFieldsMixin, ModelForm):
    readonly_fields = ('foo',)

    class Meta:
        model = Dummy
        if django.VERSION >= (1, 6):
            fields = '__all__'


class ReadOnlyFieldsMixinTestCase(TestCase):
    def test_readonly_fields_attr_empty_all_fields_should_be_readonly(self):
        form = FooModelForm()
        self.assertEqual(['bar', 'foo'], self._get_readonly_fields(form))

    def test_readonly_fields_just_defined_fields_should_be_readonly(self):
        form = BarModelForm()
        self.assertEqual(['foo', ], self._get_readonly_fields(form))

    def test_clean_all_fields_readonly(self):
        form = FooModelForm({'foo': 'FOO'})  # bar empty is invalid
        form.is_valid()
        self.assertEqual(['bar', 'foo'], self._get_fields_cleaned(form))

    def test_clean_attr_empty_all_fields_0(self):
        form = BarModelForm({'foo': 'FOO'})
        form.is_valid()
        self.assertEqual(['foo'], self._get_fields_cleaned(form))
        self.assertTrue('bar' in form.errors.keys())

    def test_clean_attr_empty_all_fields_1(self):
        form = BarModelForm({'bar': 'BAR'})
        form.is_valid()
        self.assertEqual(['bar', 'foo'], self._get_fields_cleaned(form))

    def _widget_attr_is_disabled(self, field):
        return 'disabled' in field.widget.attrs and \
               field.widget.attrs['disabled'] == 'true'

    def _is_readonly(self, field):
        return self._widget_attr_is_disabled(field) and not field.required

    def _get_readonly_fields(self, form):
        return sorted([field_name for field_name, field in six.iteritems(form.fields)
                       if self._is_readonly(field)])

    def _get_fields_cleaned(self, form):
        return sorted([field_name for field_name, field in
                       six.iteritems(form.cleaned_data)])
