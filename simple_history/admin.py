from __future__ import unicode_literals

from functools import partial
from django.core.exceptions import PermissionDenied
from django.conf.urls import patterns, url
from django.contrib.admin import helpers, ModelAdmin
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.text import capfirst
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.conf import settings

try:
    from django.contrib.admin.utils import unquote
except ImportError:  # Django < 1.7
    from django.contrib.admin.util import unquote
try:
    USER_NATURAL_KEY = settings.AUTH_USER_MODEL
except AttributeError:  # Django < 1.5
    USER_NATURAL_KEY = "auth.User"

USER_NATURAL_KEY = tuple(key.lower() for key in USER_NATURAL_KEY.split('.', 1))

settings.SIMPLE_HISTORY_EDIT = getattr(settings, 'SIMPLE_HISTORY_EDIT', False)


class SimpleHistoryAdmin(ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(SimpleHistoryAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        try:
            info = opts.app_label, opts.model_name
        except AttributeError:  # Django < 1.7
            info = opts.app_label, opts.module_name
        history_urls = patterns(
            "",
            url("^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name='%s_%s_simple_history' % info),
            url("^([^/]+)/history/([^/]+)/edit/$",
                admin_site.admin_view(self.history_form_view),
                name='%s_%s_simple_history_edit' % info,
                kwargs={"change_history": True}),
            url("^([^/]+)/history/([^/]+)/delete/$",
                admin_site.admin_view(self.history_data_delete),
                name='%s_%s_simple_history_delete' % info),
        )
        return history_urls + urls

    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = unquote(object_id)
        action_list = history.filter(**{pk_name: object_id})
        # If no history was found, see whether this object even exists.
        obj = get_object_or_404(model, pk=object_id)
        content_type = ContentType.objects.get_by_natural_key(
            *USER_NATURAL_KEY)
        admin_user_view = 'admin:%s_%s_change' % (content_type.app_label,
                                                  content_type.model)

        context = {
            'title': _('Change history: %s') % force_text(obj),
            'action_list': action_list,
            'module_name': capfirst(force_text(opts.verbose_name_plural)),
            'object': obj,
            'root_path': getattr(self.admin_site, 'root_path', None),
            'app_label': app_label,
            'opts': opts,
            'admin_user_view': admin_user_view,
            'change_history': settings.SIMPLE_HISTORY_EDIT
        }
        context.update(extra_context or {})
        return render(request, template_name=self.object_history_template,
                      dictionary=context, current_app=self.admin_site.name)

    def history_data_delete(self, request, object_id, version_id):
        original_opts = self.model._meta
        model = getattr(
            self.model,
            self.model._meta.simple_history_manager_attribute).model
        obj = get_object_or_404(model, **{
            original_opts.pk.attname: object_id,
            'history_id': version_id,
        }).instance

        verbose_name = obj._meta.verbose_name
        msg = _('The %(name)s "%(obj)s" was deleted successfully.') % {
            'name': force_text(verbose_name),
            'obj': force_text(obj)
        }

        history_obj = obj.history.get(pk=version_id)
        history_obj.delete()

        self.message_user(request, msg)

        try:
            info = original_opts.app_label, original_opts.model_name
        except AttributeError:  # Django < 1.7
            info = original_opts.app_label, original_opts.module_name

        return HttpResponseRedirect(reverse('%s_%s_simple_history' % info))

    def response_change(self, request, obj):
        if '_change_history' in request.POST and settings.SIMPLE_HISTORY_EDIT:
            verbose_name = obj._meta.verbose_name

            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
                'name': force_text(verbose_name),
                'obj': force_text(obj)
            }

            self.message_user(
                request, "%s - %s" % (msg, _("You may edit it again below")))

            return HttpResponseRedirect(request.path)
        else:
            return super(SimpleHistoryAdmin, self).response_change(
                request, obj)

    def history_form_view(
            self, request, object_id, version_id, change_history=False):

        original_opts = self.model._meta
        model = getattr(
            self.model,
            self.model._meta.simple_history_manager_attribute).model
        obj = get_object_or_404(model, **{
            original_opts.pk.attname: object_id,
            'history_id': version_id,
        }).instance
        obj._state.adding = False
        original_obj = obj

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if change_history and settings.SIMPLE_HISTORY_EDIT:
            obj = obj.history.get(pk=version_id)
            model = get_model(obj._meta.app_label, obj._meta.object_name)

        formsets = []
        form_class = self.get_form(request, obj, model)
        if request.method == 'POST':
            form = form_class(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                new_object = self.save_form(request, form, change=True)
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()

                self.log_change(request, new_object,
                                self.construct_change_message(
                                    request, form, formsets))
                return self.response_change(request, new_object)
        else:
            form = form_class(instance=obj)

        admin_form = helpers.AdminForm(
            form,
            self.get_fieldsets(request, obj, model),
            self.prepopulated_fields,
            self.get_readonly_fields(request, obj),
            model_admin=self
        )

        try:
            model_name = original_opts.model_name
        except AttributeError:  # Django < 1.7
            model_name = original_opts.module_name
        url_triplet = self.admin_site.name, original_opts.app_label, model_name

        context = {
            'title': _('Revert %s') % force_text(obj),
            'adminform': admin_form,
            'object_id': object_id,
            'original': obj,
            'original_obj': original_obj,
            'is_popup': False,
            'media': mark_safe(self.media + admin_form.media),
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': original_obj._meta.app_label,
            'original_opts': original_opts,
            'changelist_url': reverse('%s:%s_%s_changelist' % url_triplet),
            'change_url': reverse('%s:%s_%s_change' % url_triplet,
                                  args=(original_obj.pk,)),
            'history_url': reverse('%s:%s_%s_history' % url_triplet,
                                   args=(original_obj.pk,)),
            'change_history': change_history,
            'delete_url': reverse(
                '%s:%s_%s_simple_history_delete' % url_triplet,
                args=(original_obj.pk, version_id)),

            # Context variables copied from render_change_form
            'add': False,
            'change': False,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,
            'has_absolute_url': False,
            'form_url': '',
            'opts': model._meta,
            'content_type_id': ContentType.objects.get_for_model(
                self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': getattr(self.admin_site, 'root_path', None),
        }
        return render(request, template_name=self.object_history_form_template,
                      dictionary=context, current_app=self.admin_site.name)

    def save_model(self, request, obj, form, change):
        """Set special model attribute to user for reference after save"""
        obj._history_user = request.user
        super(SimpleHistoryAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, model=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
            if model and 'Historical' in model._meta.object_name:
                fieldsets = fieldsets + self.history_fieldsets
            fields = flatten_fieldsets(fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if (self.exclude is None and hasattr(self.form, '_meta')
                and self.form._meta.exclude):
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(
                self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        if model:
            return modelform_factory(model, **defaults)
        else:
            return modelform_factory(self.model, **defaults)

    def get_fieldsets(self, request, obj=None, model=None):
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
            if model and 'Historical' in model._meta.object_name:
                return fieldsets + self.history_fieldsets
            return fieldsets
        form = self.get_formset(request, obj).form
        fields = form.base_fields.keys() + list(
            self.get_readonly_fields(request, obj))
        return [(None, {'fields': fields})]
