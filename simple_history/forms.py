from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_str

__all__ = (
    'ReadOnlyFieldsMixin',
    'new_readonly_form'
)


class ReadOnlyFieldsMixin(object):
    readonly_fields = ()
    all_fields = False

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)

        for field in (field for field_name, field in six.iteritems(self.fields)
                      if field_name in self.readonly_fields
                      or self.all_fields is True):
            field.widget.attrs['disabled'] = 'true'
            field.required = False

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin, self).clean()
        if self.all_fields:
            for field_name, field in six.iteritems(self.fields):
                cleaned_data[field_name] = getattr(self.instance, field_name)
            return cleaned_data
        else:
            for field_name in self.readonly_fields:
                cleaned_data[field_name] = getattr(self.instance, field_name)
            return cleaned_data


def new_readonly_form(klass, readonly_fields=()):
    name = force_str("ReadOnly{}".format(klass.__name__))
    klass_fields = {'readonly_fields': readonly_fields}
    return type(name, (ReadOnlyFieldsMixin, klass), klass_fields)
