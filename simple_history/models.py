from __future__ import unicode_literals

import copy
import importlib
import threading
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models, router
from django.db.models import Q
from django.db.models.fields.proxy import OrderWrt
from django.urls import reverse
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.text import format_lazy
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from . import exceptions
from .manager import HistoryDescriptor
from .signals import (
    pre_create_historical_record,
    post_create_historical_record,
)

User = get_user_model()
registered_models = {}


def default_get_user(request, **kwargs):
    try:
        return request.user
    except AttributeError:
        return None


class HistoricalRecords(object):
    thread = threading.local()

    def __init__(self, verbose_name=None, bases=(models.Model,),
                 user_related_name='+', table_name=None, inherit=False,
                 excluded_fields=None, history_id_field=None,
                 history_change_reason_field=None,
                 user_model=None, get_user=default_get_user,
                 cascade_delete_history=False):
        self.user_set_verbose_name = verbose_name
        self.user_related_name = user_related_name
        self.table_name = table_name
        self.inherit = inherit
        self.history_id_field = history_id_field
        self.history_change_reason_field = history_change_reason_field
        self.user_model = user_model
        self.get_user = get_user
        self.cascade_delete_history = cascade_delete_history
        if excluded_fields is None:
            excluded_fields = []
        self.excluded_fields = excluded_fields
        try:
            if isinstance(bases, six.string_types):
                raise TypeError
            self.bases = (HistoricalChanges,) + tuple(bases)
        except TypeError:
            raise TypeError("The `bases` option must be a list or a tuple.")

    def contribute_to_class(self, cls, name):
        self.manager_name = name
        self.module = cls.__module__
        self.cls = cls
        models.signals.class_prepared.connect(self.finalize, weak=False)
        self.add_extra_methods(cls)

    def add_extra_methods(self, cls):
        def save_without_historical_record(self, *args, **kwargs):
            """
            Save model without saving a historical record

            Make sure you know what you're doing before you use this method.
            """
            self.skip_history_when_saving = True
            try:
                ret = self.save(*args, **kwargs)
            finally:
                del self.skip_history_when_saving
            return ret

        setattr(cls, 'save_without_historical_record',
                save_without_historical_record)

    def finalize(self, sender, **kwargs):
        inherited = False
        if self.cls is not sender:  # set in concrete
            inherited = (self.inherit and issubclass(sender, self.cls))
            if not inherited:
                return  # set in abstract

        if hasattr(sender._meta, 'simple_history_manager_attribute'):
            raise exceptions.MultipleRegistrationsError(
                '{}.{} registered multiple times for history tracking.'.format(
                    sender._meta.app_label,
                    sender._meta.object_name,
                )
            )
        history_model = self.create_history_model(sender, inherited)
        if inherited:
            # Make sure history model is in same module as concrete model
            module = importlib.import_module(history_model.__module__)
        else:
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

    def create_history_model(self, model, inherited):
        """
        Creates a historical model to associate with the model provided.
        """
        attrs = {
            '__module__': self.module,
            '_history_excluded_fields': self.excluded_fields
        }

        app_module = '%s.models' % model._meta.app_label

        if inherited:
            # inherited use models module
            attrs['__module__'] = model.__module__
        elif model.__module__ != self.module:
            # registered under different app
            attrs['__module__'] = self.module
        elif app_module != self.module:
            # Abuse an internal API because the app registry is loading.
            app = apps.app_configs[model._meta.app_label]
            models_module = app.name
            attrs['__module__'] = models_module

        fields = self.copy_fields(model)
        attrs.update(fields)
        attrs.update(self.get_extra_fields(model, fields))
        # type in python2 wants str as a first argument
        attrs.update(Meta=type(str('Meta'), (), self.get_meta_options(model)))
        if self.table_name is not None:
            attrs['Meta'].db_table = self.table_name
        name = 'Historical%s' % model._meta.object_name
        registered_models[model._meta.db_table] = model
        return python_2_unicode_compatible(
            type(str(name), self.bases, attrs))

    def fields_included(self, model):
        fields = []
        for field in model._meta.fields:
            if field.name not in self.excluded_fields:
                fields.append(field)
        return fields

    def copy_fields(self, model):
        """
        Creates copies of the model's original fields, returning
        a dictionary mapping field name to copied field object.
        """
        fields = {}
        for field in self.fields_included(model):
            field = copy.copy(field)
            field.remote_field = copy.copy(field.remote_field)
            if isinstance(field, OrderWrt):
                # OrderWrt is a proxy field, switch to a plain IntegerField
                field.__class__ = models.IntegerField
            if isinstance(field, models.ForeignKey):
                old_field = field
                field_arguments = {'db_constraint': False}
                if getattr(old_field, 'one_to_one', False) \
                   or isinstance(old_field, models.OneToOneField):
                    FieldType = models.ForeignKey
                else:
                    FieldType = type(old_field)
                if getattr(old_field, 'to_fields', []):
                    field_arguments['to_field'] = old_field.to_fields[0]
                if getattr(old_field, 'db_column', None):
                    field_arguments['db_column'] = old_field.db_column

                # If old_field.remote_field.model is 'self' then we have a
                # case where object has a foreign key to itself. In this case
                # we need to set the `model` value of the field to a model. We
                # can use the old_field.model value.
                if isinstance(old_field.remote_field.model, str) and \
                   old_field.remote_field.model == 'self':
                    object_to = old_field.model
                else:
                    object_to = old_field.remote_field.model

                field = FieldType(
                    object_to,
                    related_name='+',
                    null=True,
                    blank=True,
                    primary_key=False,
                    db_index=True,
                    serialize=True,
                    unique=False,
                    on_delete=models.DO_NOTHING,
                    **field_arguments
                )
                field.name = old_field.name
            else:
                transform_field(field)
            fields[field.name] = field
        return fields

    def get_extra_fields(self, model, fields):
        """Return dict of extra fields added to the historical record model"""

        user_model = self.user_model or User

        def revert_url(self):
            """URL for this change in the default admin site."""
            opts = model._meta
            app_label, model_name = opts.app_label, opts.model_name
            return reverse(
                '%s:%s_%s_simple_history' % (
                    admin.site.name,
                    app_label,
                    model_name
                ),
                args=[getattr(self, opts.pk.attname), self.history_id]
            )

        def get_instance(self):
            attrs = {
                field.attname: getattr(self, field.attname)
                for field in fields.values()
            }
            if self._history_excluded_fields:
                excluded_attnames = [
                    model._meta.get_field(field).attname
                    for field in self._history_excluded_fields
                ]
                values = model.objects.filter(
                    pk=getattr(self, model._meta.pk.attname)
                ).values(*excluded_attnames).get()
                attrs.update(values)
            return model(**attrs)

        def get_next_record(self):
            """
            Get the next history record for the instance. `None` if last.
            """
            return self.instance.history.filter(
                Q(history_date__gt=self.history_date)
            ).order_by('history_date').first()

        def get_prev_record(self):
            """
            Get the previous history record for the instance. `None` if first.
            """
            return self.instance.history.filter(
                Q(history_date__lt=self.history_date)
            ).order_by('history_date').last()

        if self.history_id_field:
            history_id_field = self.history_id_field
            history_id_field.primary_key = True
            history_id_field.editable = False
        elif getattr(settings, 'SIMPLE_HISTORY_HISTORY_ID_USE_UUID', False):
            history_id_field = models.UUIDField(
                primary_key=True, default=uuid.uuid4, editable=False
            )
        else:
            history_id_field = models.AutoField(primary_key=True)

        if self.history_change_reason_field:
            # User specific field from init
            history_change_reason_field = self.history_change_reason_field
        elif getattr(
            settings, 'SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD',
            False
        ):
            # Use text field with no max length, not enforced by DB anyways
            history_change_reason_field = models.TextField(null=True)
        else:
            # Current default, with max length
            history_change_reason_field = models.CharField(
                max_length=100, null=True
            )

        return {
            'history_id': history_id_field,
            'history_date': models.DateTimeField(),
            'history_change_reason': history_change_reason_field,
            'history_user': models.ForeignKey(
                user_model, null=True, related_name=self.user_related_name,
                on_delete=models.SET_NULL),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', _('Created')),
                ('~', _('Changed')),
                ('-', _('Deleted')),
            )),
            'history_object': HistoricalObjectDescriptor(
                model,
                self.fields_included(model)
            ),
            'instance': property(get_instance),
            'instance_type': model,
            'next_record': property(get_next_record),
            'prev_record': property(get_prev_record),
            'revert_url': revert_url,
            '__str__': lambda self: '%s as of %s' % (self.history_object,
                                                     self.history_date)
        }

    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the historical record model.
        """
        meta_fields = {
            'ordering': ('-history_date', '-history_id'),
            'get_latest_by': 'history_date',
        }
        if self.user_set_verbose_name:
            name = self.user_set_verbose_name
        else:
            name = format_lazy('historical {}',
                               smart_text(model._meta.verbose_name))
        meta_fields['verbose_name'] = name
        return meta_fields

    def post_save(self, instance, created, **kwargs):
        if not created and hasattr(instance, 'skip_history_when_saving'):
            return
        if not kwargs.get('raw', False):
            self.create_historical_record(instance, created and '+' or '~')

    def post_delete(self, instance, **kwargs):
        if self.cascade_delete_history:
            manager = getattr(instance, self.manager_name)
            manager.all().delete()
        else:
            self.create_historical_record(instance, '-')

    def create_historical_record(self, instance, history_type):
        history_date = getattr(instance, '_history_date', now())
        history_user = self.get_history_user(instance)
        history_change_reason = getattr(instance, 'changeReason', None)
        manager = getattr(instance, self.manager_name)

        pre_create_historical_record.send(
            sender=manager.model, instance=instance,
            history_date=history_date, history_user=history_user,
            history_change_reason=history_change_reason,
        )

        attrs = {}
        for field in self.fields_included(instance):
            attrs[field.attname] = getattr(instance, field.attname)
        history_instance = manager.create(
            history_date=history_date, history_type=history_type,
            history_user=history_user,
            history_change_reason=history_change_reason, **attrs
        )

        post_create_historical_record.send(
            sender=manager.model, instance=instance,
            history_instance=history_instance,
            history_date=history_date, history_user=history_user,
            history_change_reason=history_change_reason,
        )

    def get_history_user(self, instance):
        """Get the modifying user from instance or middleware."""
        try:
            return instance._history_user
        except AttributeError:
            request = None
            try:
                if self.thread.request.user.is_authenticated:
                    request = self.thread.request
            except AttributeError:
                pass

        return self.get_user(instance=instance, request=request)


def transform_field(field):
    """Customize field appropriately for use in historical model"""
    field.name = field.attname
    if isinstance(field, models.AutoField):
        field.__class__ = models.IntegerField

    elif isinstance(field, models.FileField):
        # Don't copy file, just path.
        field.__class__ = models.TextField

    # Historical instance shouldn't change create/update timestamps
    field.auto_now = False
    field.auto_now_add = False

    if field.primary_key or field.unique:
        # Unique fields can no longer be guaranteed unique,
        # but they should still be indexed for faster lookups.
        field.primary_key = False
        field._unique = False
        field.db_index = True
        field.serialize = True


class HistoricalObjectDescriptor(object):
    def __init__(self, model, fields_included):
        self.model = model
        self.fields_included = fields_included

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname)
                  for f in self.fields_included)
        return self.model(*values)


class HistoricalChanges(object):
    def diff_against(self, old_history):
        if not isinstance(old_history, type(self)):
            raise TypeError(("unsupported type(s) for diffing: "
                             "'{}' and '{}'").format(
                            type(self),
                            type(old_history)))

        changes = []
        changed_fields = []
        for field in self._meta.fields:
            if hasattr(self.instance, field.name) and \
               hasattr(old_history.instance, field.name):
                old_value = getattr(old_history, field.name, '')
                new_value = getattr(self, field.name)
                if old_value != new_value:
                    change = ModelChange(field.name, old_value, new_value)
                    changes.append(change)
                    changed_fields.append(field.name)

        return ModelDelta(changes,
                          changed_fields,
                          old_history,
                          self)


class ModelChange(object):
    def __init__(self, field_name, old_value, new_value):
        self.field = field_name
        self.old = old_value
        self.new = new_value


class ModelDelta(object):
    def __init__(self, changes, changed_fields, old_record, new_record):
        self.changes = changes
        self.changed_fields = changed_fields
        self.old_record = old_record
        self.new_record = new_record
