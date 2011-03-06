from django import template
from django.db import models
from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.admin.util import unquote
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode


class SimpleHistoryAdmin(admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"

    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        action_list = model.history.filter(id=object_id)
        # If no history was found, see whether this object even exists.
        obj = get_object_or_404(model, pk=unquote(object_id))
        context = {
            'title': _('Change history: %s') % force_unicode(obj),
            'action_list': action_list,
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.object_history_template, context, context_instance=context_instance)
