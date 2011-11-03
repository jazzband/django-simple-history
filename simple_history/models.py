import copy
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import importlib
from manager import HistoryDescriptor


class HistoricalRecords(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        self.module = cls.__module__
        models.signals.class_prepared.connect(self.finalize, sender=cls)

        def save_without_historical_record(self, *args, **kwargs):
            """Caution! Make sure you know what you're doing before you use this method."""
            self.skip_history_when_saving = True
            ret = self.save(*args, **kwargs)
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

        fields = self.copy_fields(model)
        attrs.update(fields)
        attrs.update(self.get_extra_fields(model, fields))
        attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))
        name = 'Historical%s' % model._meta.object_name
        return type(name, (models.Model,), attrs)

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

            if isinstance(field, models.ForeignKey):
                field.__class__ = models.IntegerField
                #ughhhh. open to suggestions here
                try:
                    field.rel = None
                except:
                    pass
                try:
                    field.related = None
                except:
                    pass
                try:
                    field.related_query_name = None
                except:
                    pass
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
            'history_user': models.ForeignKey(User, null=True),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', 'Created'),
                ('~', 'Changed'),
                ('-', 'Deleted'),
            )),
            'history_object': HistoricalObjectDescriptor(model),
            'instance': property(get_instance),
            'revert_url': revert_url,
            '__unicode__': lambda self: u'%s as of %s' % (self.history_object,
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
