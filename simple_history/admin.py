from __future__ import unicode_literals

from django import http
from django.apps import apps as django_apps
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.utils import unquote
from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

USER_NATURAL_KEY = tuple(key.lower()
                         for key in settings.AUTH_USER_MODEL.split(".", 1))


class HistoricalPermissionsModelAdminMixin(object):
    @property
    def historical_permissions_enabled(self):
        """Returns True/False based on settings attr.

        Defaults to False.
        """
        try:
            enabled = settings.SIMPLE_HISTORY_PERMISSIONS_ENABLED
        except AttributeError:
            enabled = False
        return enabled

    def _has_historical_permission(self, request, action, obj=None):
        historical_opts = self.history_manager.model._meta
        historical_codename = get_permission_codename(action, historical_opts)
        try:
            func = getattr(self, "has_%s_permission" % action)
        except AttributeError:
            permission = False
        else:
            permission = func(request, obj)
        historical_permission = request.user.has_perm(
            "%s.%s" % (historical_opts.app_label, historical_codename)
        )
        return permission and historical_permission

    def has_historical_view_permission(self, request, obj=None):
        if self.historical_permissions_enabled:
            view_permission = self._has_historical_permission(
                request, "view", obj)
        else:
            try:
                view_permission = self.has_view_permission(request, obj)
            except AttributeError:
                view_permission = self.has_change_permission(request, obj)
        return view_permission

    def has_historical_change_permission(self, request, obj=None):
        if self.historical_permissions_enabled:
            change_permission = self._has_historical_permission(
                request, "change", obj)
        else:
            change_permission = self.has_change_permission(request, obj)
        return change_permission

    def has_historical_view_or_change_permission(self, request, obj=None):
        if self.historical_permissions_enabled:
            has_permission = self.has_historical_view_permission(
                request, obj
            ) or self.has_historical_change_permission(request, obj)
        else:
            try:
                has_permission = self.has_view_or_change_permission(
                    request, obj)
            except AttributeError:
                has_permission = self.has_change_permission(request, obj)
        return has_permission

    def revert_disabled(self, request, obj):
        """Returns `True` or `False` based on settings attr.

        Note:
          * Always returns `False` if user is a superuser
          * setting attr to False does not override user perms
        """
        if request.user.is_superuser:
            revert_disabled = False
        else:
            revert_disabled = getattr(
                settings, "SIMPLE_HISTORY_REVERT_DISABLED", False)
        return revert_disabled

    def has_revert_permission(self, request, obj):
        """Returns `True` if user has permission to revert
        a model instance to a previous version in its
        history.
        """
        if self.revert_disabled(request, obj):
            permission = False
        else:
            permission = self.has_historical_change_permission(request, obj)
        return permission


class SimpleHistoryAdmin(HistoricalPermissionsModelAdminMixin, admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin.
        """
        urls = super(SimpleHistoryAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        history_urls = [
            url(
                "^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name="%s_%s_simple_history" % info,
            )
        ]
        return history_urls + urls

    def history_view(self, request, object_id, extra_context=None):
        """Overridden `history_view`.
        """
        request.current_app = self.admin_site.name
        opts = self.model._meta
        object_id = unquote(object_id)
        object_history = self.get_object_history(object_id)
        obj = self.get_object(request, object_id,
                              object_history=object_history)
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        if not self.has_historical_view_or_change_permission(request, obj):
            raise PermissionDenied

        title = (
            _("Change history: %s")
            if self.has_revert_permission(request, obj)
            else _("View history: %s")
        )

        context = {
            "title": title % force_text(obj),
            "action_list": object_history,
            "module_name": capfirst(force_text(opts.verbose_name_plural)),
            "object": obj,
            "root_path": getattr(self.admin_site, "root_path", None),
            "app_label": opts.app_label,
            "opts": opts,
            "admin_user_view": self.admin_user_view,
            "history_list_display": self.get_history_list_display(),
            "has_change_permission": self.has_historical_change_permission(
                request, obj
            ),
            "has_revert_permission": self.has_revert_permission(request, obj),
        }
        context.update(self.admin_site.each_context(request))
        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )

    def get_object(self, request, object_id, object_history=None, **kwargs):
        """Returns the model instance or None

        If None, attempts to get the instance from history.
        """
        obj = super(SimpleHistoryAdmin, self).get_object(
            request, object_id, **kwargs)
        if not obj and object_history:
            try:
                obj = object_history.latest("history_date").instance
            except ObjectDoesNotExist:
                pass
        return obj

    def get_object_history(self, object_id):
        """Returns a queryset of historical instances.
        """
        queryset = self.history_manager.filter(
            **{self.model._meta.pk.attname: object_id}
        )
        if not isinstance(self.history_manager.model.history_user, property):
            queryset = queryset.select_related("history_user")
        return self.fetch_history_list_display_callables(queryset)

    @property
    def history_manager(self):
        """Returns the HistoricalManager instance.
        """
        return getattr(self.model, self.model._meta.simple_history_manager_attribute)

    def fetch_history_list_display_callables(self, queryset):
        """Returns a queryset after setting, on each instance,
        the value of any callables from `history_list_display`.
        """
        callable_attrs = self.history_list_display_callables
        if callable_attrs:
            for obj in queryset:
                for attrname, attr in callable_attrs:
                    setattr(obj, attrname, attr(obj))
        return queryset

    def get_history_list_display(self):
        """Returns a list.
        """
        try:
            return self.history_list_display
        except AttributeError:
            return []

    @property
    def history_list_display_callables(self):
        """Returns a list of callable attributes on `self`
        referred to in `history_list_display`.
        """
        callable_attrs = []
        for attrname in self.get_history_list_display():
            attr = getattr(self, attrname, None)
            if callable(attr):
                callable_attrs.append((attrname, attr))
        return callable_attrs

    @property
    def admin_user_view(self):
        content_type = self.content_type_model_cls.objects.get_by_natural_key(
            *USER_NATURAL_KEY
        )
        return "admin:%s_%s_change" % (content_type.app_label, content_type.model)

    @property
    def change_history(self):
        try:
            change_history = settings.SIMPLE_HISTORY_EDIT
        except AttributeError:
            change_history = False
        return change_history

    def response_change(self, request, obj):
        if self.change_history and "_change_history" in request.POST:
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
                "name": force_text(obj._meta.verbose_name),
                "obj": force_text(obj),
            }
            self.message_user(
                request, "%s - %s" % (msg, _("You may edit it again below"))
            )
            return http.HttpResponseRedirect(request.path)
        else:
            return super(SimpleHistoryAdmin, self).response_change(request, obj)

    def history_form_view(self, request, object_id, version_id, extra_context=None):
        request.current_app = self.admin_site.name
        original_opts = self.model._meta
        model = self.history_manager.model
        obj = get_object_or_404(
            model, **{original_opts.pk.attname: object_id, "history_id": version_id}
        ).instance
        obj._state.adding = False

        if not self.has_historical_view_or_change_permission(request, obj):
            raise PermissionDenied

        if "_change_history" in request.POST and self.change_history:
            obj = obj.history.get(pk=version_id).instance

        formsets = []
        form_class = self.get_form(request, obj)
        if request.method == "POST":
            form = form_class(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                new_object = self.save_form(request, form, change=True)
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()

                self.log_change(
                    request,
                    new_object,
                    self.construct_change_message(request, form, formsets),
                )
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

        title = (
            _("Revert %s") if self.has_revert_permission(
                request, obj) else _("View %s")
        )

        model_name = original_opts.model_name
        url_triplet = self.admin_site.name, original_opts.app_label, model_name
        context = {
            "title": title % force_text(obj),
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": False,
            "media": mark_safe(self.media + admin_form.media),
            "errors": helpers.AdminErrorList(form, formsets),
            "app_label": original_opts.app_label,
            "original_opts": original_opts,
            "changelist_url": reverse("%s:%s_%s_changelist" % url_triplet),
            "change_url": reverse("%s:%s_%s_change" % url_triplet, args=(obj.pk,)),
            "history_url": reverse("%s:%s_%s_history" % url_triplet, args=(obj.pk,)),
            "change_history": self.change_history,
            # Context variables copied from render_change_form
            "add": False,
            "change": True,
            "has_view_permission": self.has_historical_view_permission(request, obj),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_historical_change_permission(
                request, obj
            ),
            "has_delete_permission": self.has_delete_permission(request, obj),
            "has_revert_permission": self.has_revert_permission(request, obj),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": model._meta,
            "content_type_id": self.content_type_model_cls.objects.get_for_model(
                self.model
            ).id,
            "save_as": self.save_as,
            "save_on_top": self.save_on_top,
            "root_path": getattr(self.admin_site, "root_path", None),
        }
        context.update(self.admin_site.each_context(request))
        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_form_template, context, **extra_kwargs
        )

    def render_history_view(self, request, template, context, **kwargs):
        """Catch call to render, to allow overriding.
        """
        return render(request, template, context, **kwargs)

    def history_form_view_title(self, request, obj):
        """Returns a "revert" or "view" title string rendered
        relative to the user's permissions.
        """
        if self.has_revert_permission(request, obj):
            title = _("Revert %s")
        else:
            title = _("View %s")
        return title % force_text(obj)

    def save_model(self, request, obj, form, change):
        """Set special model attribute to user for reference after save.
        """
        obj._history_user = request.user
        super(SimpleHistoryAdmin, self).save_model(request, obj, form, change)

    @property
    def content_type_model_cls(self):
        """Returns the ContentType model class.
        """
        return django_apps.get_model("contenttypes.contenttype")
