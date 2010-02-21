import copy
import datetime

from django.db import models

from chapter11.current_user import models as current_user
from chapter11.history import manager

class HistoricalRecords(object):
    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        history_model = self.create_history_model(sender)

        # The HistoricalRecords object will be discarded,
        # so the signal handlers can't use weak references.
        models.signals.post_save.connect(self.post_save, sender=sender,
                                         weak=False)
        models.signals.post_delete.connect(self.post_delete, sender=sender,
                                           weak=False)

        descriptor = manager.HistoryDescriptor(history_model)
        setattr(sender, self.manager_name, descriptor)

    def create_history_model(self, model):
        """
        Creates a historical model to associate with the model provided.
        """
        attrs = self.copy_fields(model)
        attrs.update(self.get_extra_fields(model))
        attrs.update(Meta=type('Meta', (), self.get_meta_options(model)))
        name = 'Historical%s' % model._meta.object_name
        return type(name, (models.Model,), attrs)

    def copy_fields(self, model):
        """
        Creates copies of the model's original fields, returning
        a dictionary mapping field name to copied field object.
        """
        # Though not strictly a field, this attribute
        # is required for a model to function properly.
        fields = {'__module__': model.__module__}

        for field in model._meta.fields:
            field = copy.copy(field)

            if isinstance(field, models.AutoField):
                # The historical model gets its own AutoField, so any
                # existing one must be replaced with an IntegerField.
                field.__class__ = models.IntegerField

            if field.primary_key or field.unique:
                # Unique fields can no longer be guaranteed unique,
                # but they should still be indexed for faster lookups.
                field.primary_key = False
                field._unique = False
                field.db_index = True
            fields[field.name] = field

        return fields

    def get_extra_fields(self, model):
        """
        Returns a dictionary of fields that will be added to the historical
        record model, in addition to the ones returned by copy_fields below.
        """
        rel_nm = '_%s_history' % model._meta.object_name.lower()
        return {
            'history_id': models.AutoField(primary_key=True),
            'history_date': models.DateTimeField(default=datetime.datetime.now),
            'history_user': current_user.CurrentUserField(related_name=rel_nm),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', 'Created'),
                ('~', 'Changed'),
                ('-', 'Deleted'),
            )),
            'history_object': HistoricalObjectDescriptor(model),
            '__unicode__': lambda self: u'%s as of %s' % (self.history_object,
                                                          self.history_date)
        }

    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the historical record model.
        """
        return {
            'ordering': ('-history_date',),
        }

    def post_save(self, instance, created, **kwargs):
        self.create_historical_record(instance, created and '+' or '~')

    def post_delete(self, instance, **kwargs):
        self.create_historical_record(instance, '-')

    def create_historical_record(self, instance, type):
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        manager.create(history_type=type, **attrs)

class HistoricalObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname) for f in self.model._meta.fields)
        return self.model(*values)
