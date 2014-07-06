from __future__ import unicode_literals

import re
import difflib
from django import template
from django.core.exceptions import PermissionDenied
try:
    from django.conf.urls import patterns, url
except ImportError:  # pragma: no cover
    from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.util import unquote
from django.utils.text import capfirst
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _
try:
    from django.utils.encoding import force_text
except ImportError:  # pragma: no cover, django 1.3 compatibility
    from django.utils.encoding import force_unicode as force_text
from django.conf import settings

try:
    USER_NATURAL_KEY = settings.AUTH_USER_MODEL
except AttributeError:
    USER_NATURAL_KEY = "auth.User"
USER_NATURAL_KEY = tuple(key.lower() for key in USER_NATURAL_KEY.split('.', 1))


class SimpleHistoryAdmin(admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"
    object_compare_template = "simple_history/history_compare.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(SimpleHistoryAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        try:
            info = opts.app_label, opts.module_name
        except AttributeError:  # pragma: no cover
            info = opts.app_label, opts.model_name
        history_urls = patterns(
            "",
            url("^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name='%s_%s_simple_history' % info),
            url("^([^/]+)/compare/$",
                admin_site.admin_view(self.compare_view),
                name='%s_%s_simple_compare' % info),
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
            'admin_user_view': admin_user_view
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(
            request, current_app=self.admin_site.name)
        return render(request, self.object_history_template,
                      dictionary=context, context_instance=context_instance)

    def history_form_view(self, request, object_id, version_id):
        original_model = self.model
        original_opts = original_model._meta
        history = getattr(self.model,
                          self.model._meta.simple_history_manager_attribute)
        model = history.model
        opts = model._meta
        pk_name = original_opts.pk.attname
        record = get_object_or_404(model, **{
            pk_name: object_id,
            'history_id': version_id,
        })
        obj = record.instance
        obj._state.adding = False

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        formsets = []
        form_class = self.get_form(request, obj)
        if request.method == 'POST':
            form = form_class(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj

            if form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()

                change_message = self.construct_change_message(request, form,
                                                               formsets)
                self.log_change(request, new_object, change_message)
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
        media = self.media + admin_form.media

        try:
            model_name = original_opts.module_name
        except AttributeError:  # pragma: no cover
            model_name = original_opts.model_name
        url_triplet = self.admin_site.name, original_opts.app_label, model_name
        content_type_id = ContentType.objects.get_for_model(self.model).id
        context = {
            'title': _('Revert %s') % force_text(obj),
            'adminform': admin_form,
            'object_id': object_id,
            'original': obj,
            'is_popup': False,
            'media': mark_safe(media),
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'original_opts': original_opts,
            'changelist_url': reverse('%s:%s_%s_changelist' % url_triplet),
            'change_url': reverse('%s:%s_%s_change' % url_triplet,
                                  args=(obj.pk,)),
            'history_url': reverse('%s:%s_%s_history' % url_triplet,
                                   args=(obj.pk,)),
            # Context variables copied from render_change_form
            'add': False,
            'change': True,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,
            'has_absolute_url': False,
            'form_url': '',
            'opts': opts,
            'content_type_id': content_type_id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': getattr(self.admin_site, 'root_path', None),
        }
        context_instance = template.RequestContext(
            request,
            current_app=self.admin_site.name,
        )
        return render(request, self.object_history_form_template,
                      dictionary=context, context_instance=context_instance)

    def compare_view(self, request, object_id, extra_context=None):
        object_id = unquote(object_id)
        obj = get_object_or_404(self.model, pk=object_id)
        history = getattr(obj,
                          self.model._meta.simple_history_manager_attribute)
        prev = history.get(pk=request.GET['from'])
        curr = history.get(pk=request.GET['to'])

        fields = [{
            'name': field.attname,
            'content': getattr(curr, field.attname),
            'compare_nodes': self._get_delta_nodes(
                getattr(prev, field.attname), getattr(curr, field.attname)),
        } for field in self.model._meta.fields]
        opts = self.model._meta
        d = {
            'title': _('Compare %s') % force_text(obj),
            'app_label': opts.app_label,
            'module_name': capfirst(force_text(opts.verbose_name_plural)),
            'object_id': object_id,
            'object': obj,
            'history_bef': prev,
            'history_aft': curr,
            'fields': fields,
            'opts': opts,
            'add': False,
            'change': False,
            'show_delete': False,
            'is_popup': False,
            'save_as': self.save_as,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
        }
        return render(request, template_name=self.object_compare_template,
                      current_app=self.admin_site.name, dictionary=d)

    @staticmethod
    def _get_delta_nodes(a, b):
        delta_nodes = []
        try:
            a = re.split("(\W)", a)
            b = re.split("(\W)", b)
        except TypeError:
            if a != b:
                return [('removed', a), ('added', b)]
            return [('unchanged', b)]
        prev_a_start, prev_b_start, prev_len = (0, 0, 0)
        for block in difflib.SequenceMatcher(a=a, b=b).get_matching_blocks():
            a_start, b_start, length = block
            removed = "".join(a[prev_a_start + prev_len:a_start])
            added = "".join(b[prev_b_start + prev_len:b_start])
            same = "".join(b[b_start:b_start + length])
            if removed:
                delta_nodes.append(('removed', removed))
            if added:
                delta_nodes.append(('added', added))
            if same:
                delta_nodes.append(('unchanged', same))
            prev_a_start, prev_b_start, prev_len = block
        return delta_nodes

    def save_model(self, request, obj, form, change):
        """Set special model attribute to user for reference after save"""
        obj._history_user = request.user
        super(SimpleHistoryAdmin, self).save_model(request, obj, form, change)
