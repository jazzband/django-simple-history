from __future__ import unicode_literals

from django import http
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

USER_NATURAL_KEY = tuple(
    key.lower() for key in settings.AUTH_USER_MODEL.split('.', 1))

SIMPLE_HISTORY_EDIT = getattr(settings, 'SIMPLE_HISTORY_EDIT', False)


class SimpleHistoryAdmin(admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(SimpleHistoryAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        history_urls = [
            url("^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name='%s_%s_simple_history' % info),
        ]
        return history_urls + urls

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        request.current_app = self.admin_site.name
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = unquote(object_id)
        action_list = history.filter(**{pk_name: object_id})
        history_list_display = getattr(self, "history_list_display", [])
        # If no history was found, see whether this object even exists.
        try:
            obj = self.get_queryset(request).get(**{pk_name: object_id})
        except model.DoesNotExist:
            try:
                obj = action_list.latest('history_date').instance
            except action_list.model.DoesNotExist:
                raise http.Http404

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        # Set attribute on each action_list entry from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for list_entry in action_list:
                    setattr(list_entry, history_list_entry,
                            value_for_entry(list_entry))

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
            'history_list_display': history_list_display,
        }
        context.update(extra_context or {})
        extra_kwargs = {}
        return render(request, self.object_history_template, context,
                      **extra_kwargs)

    def response_change(self, request, obj):
        if '_change_history' in request.POST and SIMPLE_HISTORY_EDIT:
            verbose_name = obj._meta.verbose_name

            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
                'name': force_text(verbose_name),
                'obj': force_text(obj)
            }

            self.message_user(
                request, "%s - %s" % (msg, _("You may edit it again below")))

            return http.HttpResponseRedirect(request.path)
        else:
            return super(SimpleHistoryAdmin, self).response_change(
                request, obj)

    def history_form_view(self, request, object_id, version_id):
        request.current_app = self.admin_site.name
        original_opts = self.model._meta
        model = getattr(
            self.model,
            self.model._meta.simple_history_manager_attribute).model
        obj = get_object_or_404(model, **{
            original_opts.pk.attname: object_id,
            'history_id': version_id,
        }).instance
        obj._state.adding = False

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if SIMPLE_HISTORY_EDIT:
            change_history = True
        else:
            change_history = False

        if '_change_history' in request.POST and SIMPLE_HISTORY_EDIT:
            obj = obj.history.get(pk=version_id).instance

        formsets = []
        form_class = self.get_form(request, obj)
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
            self.get_fieldsets(request, obj),
            self.prepopulated_fields,
            self.get_readonly_fields(request, obj),
            model_admin=self,
        )

        model_name = original_opts.model_name
        url_triplet = self.admin_site.name, original_opts.app_label, model_name
        context = {
            'title': _('Revert %s') % force_text(obj),
            'adminform': admin_form,
            'object_id': object_id,
            'original': obj,
            'is_popup': False,
            'media': mark_safe(self.media + admin_form.media),
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': original_opts.app_label,
            'original_opts': original_opts,
            'changelist_url': reverse('%s:%s_%s_changelist' % url_triplet),
            'change_url': reverse('%s:%s_%s_change' % url_triplet,
                                  args=(obj.pk,)),
            'history_url': reverse('%s:%s_%s_history' % url_triplet,
                                   args=(obj.pk,)),
            'change_history': change_history,

            # Context variables copied from render_change_form
            'add': False,
            'change': True,
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
        extra_kwargs = {}
        return render(request, self.object_history_form_template, context,
                      **extra_kwargs)

    def save_model(self, request, obj, form, change):
        """Set special model attribute to user for reference after save"""
        obj._history_user = request.user
        super(SimpleHistoryAdmin, self).save_model(request, obj, form, change)
