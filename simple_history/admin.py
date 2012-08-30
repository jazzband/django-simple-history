from django import template
from django.core.exceptions import PermissionDenied
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.admin.util import unquote
from django.utils.text import capfirst
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode


class SimpleHistoryAdmin(admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(SimpleHistoryAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        history_urls = patterns("",
            url("^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name='%s_%s_simple_history' % info),)
        return history_urls + urls

    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        action_list = history.filter(**{pk_name: object_id})
        # If no history was found, see whether this object even exists.
        obj = get_object_or_404(model, pk=unquote(object_id))
        context = {
            'title': _('Change history: %s') % force_unicode(obj),
            'action_list': action_list,
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'root_path': getattr(self.admin_site, 'root_path', None),
            'app_label': app_label,
            'opts': opts
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.object_history_template, context, context_instance=context_instance)

    def history_form_view(self, request, object_id, version_id):
        original_model = self.model
        original_opts = original_model._meta
        history = getattr(self.model, self.model._meta.simple_history_manager_attribute)
        model = history.model
        opts = model._meta
        pk_name = original_opts.pk.attname
        record = get_object_or_404(model, **{pk_name: object_id, 'history_id': version_id})
        obj = record.instance
        obj._state.adding = False

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if request.method == 'POST' and '_saveas_new' in request.POST:
            return self.add_view(request, form_url='../add/')

        formsets = []
        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}

            if form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        url_triplet = (self.admin_site.name, original_opts.app_label,
                            original_opts.module_name)
        context = {
            'title': _('Revert %s') % force_unicode(obj),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': False,
            'media': mark_safe(media),
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'original_opts': original_opts,
            'changelist_url': reverse('%s:%s_%s_changelist' % url_triplet),
            'change_url': reverse('%s:%s_%s_change' % url_triplet, args=(obj.pk,)),
            'history_url': reverse('%s:%s_%s_history' % url_triplet, args=(obj.pk,)),
            # Context variables copied from render_change_form
            'add': False,
            'change': True,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,
            'has_absolute_url': False,
            'ordered_objects': opts.get_ordered_objects(),
            'form_url': '',
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': getattr(self.admin_site, 'root_path', None),
        }
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.object_history_form_template, context, context_instance)

    def save_model(self, request, obj, form, change):
        """
        Add the admin user to a special model attribute for reference after save
        """
        obj._history_user = request.user
        super(SimpleHistoryAdmin, self).save_model(request, obj, form, change)
