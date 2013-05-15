from __future__ import unicode_literals

import copy
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.utils import importlib
from .manager import HistoryDescriptor

try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:  # django 1.3 compatibility
    import sys

    # copy of django function without use of six
    def python_2_unicode_compatible(klass):
        """
        A decorator that defines __unicode__ and __str__ methods under Python 2.
        Under Python 3 it does nothing.

        To support Python 2 and 3 with a single code base, define a __str__ method
        returning text and apply this decorator to the class.
        """
        if sys.version_info[0] != 3:
            klass.__unicode__ = klass.__str__
            klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
        return klass


registered_models = {}


class HistoricalRecords(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        self.module = cls.__module__
        models.signals.class_prepared.connect(self.finalize, sender=cls)

        def save_without_historical_record(self, *args, **kwargs):
            """Caution! Make sure you know what you're doing before you use this method."""
            self.skip_history_when_saving = True
            try:
                ret = self.save(*args, **kwargs)
            finally:
                del self.skip_history_when_saving
            return ret
        setattr(cls, 'save_without_historical_record', save_without_historical_record)

    def finalize(self, sender, **kwargs):
        history_model = self.create_history_model(sender)
        module = importlib.import_module(self.module)
        setattr(module, history_model.__name__, history_model)

        # The HistoricalRecords object will be discarded,
        # so the signal handlers can't use weak references.
        models.signals.post_save.connect(self.post_save, sender=sender,
                                         weak=False)
        models.signals.post_delete.connect(self.post_delete, sender=sender,
                                           weak=False)

        descriptor = HistoryDescriptor(history_model)
        setattr(sender, self.manager_name, descriptor)
        sender._meta.simple_history_manager_attribute = self.manager_name

    def create_history_model(self, model):
        """
        Creates a historical model to associate with the model provided.
        """
        attrs = {'__module__': self.module}

        app_module = '%s.models' % model._meta.app_label
        if model.__module__ != self.module:
            # registered under different app
            attrs['__module__'] = self.module
        elif app_module != self.module:
            # has meta options with app_label
            app = models.get_app(model._meta.app_label)
            attrs['__module__'] = app.__name__ # full dotted name

        fields = self.copy_fields(model)
        attrs.update(fields)
        attrs.update(self.get_extra_fields(model, fields))
        # type in python2 wants str as a first argument
        attrs.update(Meta=type(str('Meta'), (), self.get_meta_options(model)))
        name = 'Historical%s' % model._meta.object_name
        registered_models[model._meta.db_table] = model
        return python_2_unicode_compatible(type(str(name), (models.Model,), attrs))

    def copy_fields(self, model):
        """
        Creates copies of the model's original fields, returning
        a dictionary mapping field name to copied field object.
        """
        fields = {}

        for field in model._meta.fields:
            field = copy.copy(field)
            fk = None

            if isinstance(field, models.AutoField):
                # The historical model gets its own AutoField, so any
                # existing one must be replaced with an IntegerField.
                field.__class__ = models.IntegerField

            if isinstance(field, models.FileField):
                # Don't copy file, just path.
                field.__class__ = models.TextField

            if isinstance(field, models.ForeignKey):
                field.__class__ = models.IntegerField
                #ughhhh. open to suggestions here
                field.rel = None
                field.related = None
                field.related_query_name = None
                field.null = True
                field.blank = True
                fk = True
            else:
                fk = False

            # The historical instance should not change creation/modification timestamps.
            field.auto_now = False
            field.auto_now_add = False

            if field.primary_key or field.unique:
                # Unique fields can no longer be guaranteed unique,
                # but they should still be indexed for faster lookups.
                field.primary_key = False
                field._unique = False
                field.db_index = True
                field.serialize = True
            if fk:
                field.name = field.name + "_id"
            fields[field.name] = field

        return fields

    def get_extra_fields(self, model, fields):
        """
        Returns a dictionary of fields that will be added to the historical
        record model, in addition to the ones returned by copy_fields below.
        """
        @models.permalink
        def revert_url(self):
            opts = model._meta
            return ('%s:%s_%s_simple_history' %
                    (admin.site.name, opts.app_label, opts.module_name),
                    [getattr(self, opts.pk.attname), self.history_id])
        def get_instance(self):
            return model(**dict([(k, getattr(self, k)) for k in fields]))

        return {
            'history_id': models.AutoField(primary_key=True),
            'history_date': models.DateTimeField(auto_now_add=True),
            'history_user': models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', 'Created'),
                ('~', 'Changed'),
                ('-', 'Deleted'),
            )),
            'history_object': HistoricalObjectDescriptor(model),
            'instance': property(get_instance),
            'revert_url': revert_url,
            '__str__': lambda self: '%s as of %s' % (self.history_object,
                                                     self.history_date)
        }

    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the historical record model.
        """
        return {
            'ordering': ('-history_date', '-history_id'),
        }

    def post_save(self, instance, created, **kwargs):
        if not created and hasattr(instance, 'skip_history_when_saving'):
            return
        if not kwargs.get('raw', False):
            self.create_historical_record(instance, created and '+' or '~')

    def post_delete(self, instance, **kwargs):
        self.create_historical_record(instance, '-')

    def create_historical_record(self, instance, type):
        history_user = getattr(instance, '_history_user', None)
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        manager.create(history_type=type, history_user=history_user, **attrs)


class HistoricalObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        return self.model(*values)
