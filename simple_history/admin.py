from django import http
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.utils import quote, unquote
from django.contrib.auth import get_permission_codename, get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.urls import re_path, reverse
from django.utils.encoding import force_str
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext as _

from .utils import get_history_manager_for_model, get_history_model_for_model

SIMPLE_HISTORY_EDIT = getattr(settings, "SIMPLE_HISTORY_EDIT", False)


class SimpleHistoryAdmin(admin.ModelAdmin):
    object_history_template = "simple_history/object_history.html"
    object_history_form_template = "simple_history/object_history_form.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super().get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        history_urls = [
            re_path(
                "^([^/]+)/history/([^/]+)/$",
                admin_site.admin_view(self.history_form_view),
                name="%s_%s_simple_history" % info,
            )
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
        if not isinstance(history.model.history_user, property):
            # Only select_related when history_user is a ForeignKey (not a property)
            action_list = action_list.select_related("history_user")
        history_list_display = getattr(self, "history_list_display", [])
        # If no history was found, see whether this object even exists.
        try:
            obj = self.get_queryset(request).get(**{pk_name: object_id})
        except model.DoesNotExist:
            try:
                obj = action_list.latest("history_date").instance
            except action_list.model.DoesNotExist:
                raise http.Http404

        if not self.has_view_history_or_change_history_permission(request, obj):
            raise PermissionDenied

        # Set attribute on each action_list entry from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for list_entry in action_list:
                    setattr(list_entry, history_list_entry, value_for_entry(list_entry))

        content_type = self.content_type_model_cls.objects.get_for_model(
            get_user_model()
        )

        admin_user_view = "admin:{}_{}_change".format(
            content_type.app_label,
            content_type.model,
        )
        context = {
            "title": self.history_view_title(request, obj),
            "action_list": action_list,
            "module_name": capfirst(force_str(opts.verbose_name_plural)),
            "object": obj,
            "root_path": getattr(self.admin_site, "root_path", None),
            "app_label": app_label,
            "opts": opts,
            "admin_user_view": admin_user_view,
            "history_list_display": history_list_display,
            "revert_disabled": self.revert_disabled(request, obj),
        }
        context.update(self.admin_site.each_context(request))
        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )

    def history_view_title(self, request, obj):
        if self.revert_disabled(request, obj) and not SIMPLE_HISTORY_EDIT:
            return _("View history: %s") % force_str(obj)
        else:
            return _("Change history: %s") % force_str(obj)

    def response_change(self, request, obj):
        if "_change_history" in request.POST and SIMPLE_HISTORY_EDIT:
            verbose_name = obj._meta.verbose_name

            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
                "name": force_str(verbose_name),
                "obj": force_str(obj),
            }

            self.message_user(
                request, "{} - {}".format(msg, _("You may edit it again below"))
            )

            return http.HttpResponseRedirect(request.path)
        else:
            return super().response_change(request, obj)

    def history_form_view(self, request, object_id, version_id, extra_context=None):
        request.current_app = self.admin_site.name
        original_opts = self.model._meta
        model = getattr(
            self.model, self.model._meta.simple_history_manager_attribute
        ).model
        obj = get_object_or_404(
            model, **{original_opts.pk.attname: object_id, "history_id": version_id}
        ).instance
        obj._state.adding = False

        if not self.has_view_history_or_change_history_permission(request, obj):
            raise PermissionDenied

        if SIMPLE_HISTORY_EDIT:
            change_history = True
        else:
            change_history = False

        if "_change_history" in request.POST and SIMPLE_HISTORY_EDIT:
            history = get_history_manager_for_model(obj)
            obj = history.get(pk=version_id).instance

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

        model_name = original_opts.model_name
        url_triplet = self.admin_site.name, original_opts.app_label, model_name
        context = {
            "title": self.history_form_view_title(request, obj),
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
            "change_history": change_history,
            "revert_disabled": self.revert_disabled(request, obj),
            # Context variables copied from render_change_form
            "add": False,
            "change": True,
            "has_add_permission": self.has_add_permission(request),
            "has_view_permission": self.has_view_history_permission(request, obj),
            "has_change_permission": self.has_change_history_permission(request, obj),
            "has_delete_permission": self.has_delete_permission(request, obj),
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

    def history_form_view_title(self, request, obj):
        if self.revert_disabled(request, obj):
            return _("View %s") % force_str(obj)
        else:
            return _("Revert %s") % force_str(obj)

    def render_history_view(self, request, template, context, **kwargs):
        """Catch call to render, to allow overriding."""
        return render(request, template, context, **kwargs)

    def save_model(self, request, obj, form, change):
        """Set special model attribute to user for reference after save"""
        obj._history_user = request.user
        super().save_model(request, obj, form, change)

    @property
    def content_type_model_cls(self):
        """Returns the ContentType model class."""
        return django_apps.get_model("contenttypes.contenttype")

    def revert_disabled(self, request, obj=None):
        """If `True`, hides the "Revert" button in the `submit_line.html` template."""
        if getattr(settings, "SIMPLE_HISTORY_REVERT_DISABLED", False):
            return True
        elif self.has_view_history_permission(
            request, obj
        ) and not self.has_change_history_permission(request, obj):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj)

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj) or self.has_change_permission(
            request, obj
        )

    def has_view_history_or_change_history_permission(self, request, obj=None):
        if self.enforce_history_permissions:
            return self.has_view_history_permission(
                request, obj
            ) or self.has_change_history_permission(request, obj)
        return self.has_view_or_change_permission(request, obj)

    def has_view_history_permission(self, request, obj=None):
        if self.enforce_history_permissions:
            opts_history = get_history_model_for_model(self.model)._meta
            codename_view_history = get_permission_codename("view", opts_history)
            return request.user.has_perm(
                f"{opts_history.app_label}.{codename_view_history}"
            )
        return self.has_view_permission(request, obj)

    def has_change_history_permission(self, request, obj=None):
        if self.enforce_history_permissions:
            opts_history = get_history_model_for_model(self.model)._meta
            codename_change_history = get_permission_codename("change", opts_history)
            return request.user.has_perm(
                f"{opts_history.app_label}.{codename_change_history}"
            )
        return self.has_change_permission(request, obj)

    @property
    def enforce_history_permissions(self):
        return getattr(
            settings, "SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS", False
        )


class SimpleHistoryWithDeletedAdmin(SimpleHistoryAdmin):
    class SimpleHistoryShowDeletedFilter(admin.SimpleListFilter):
        title = "Entries"
        parameter_name = "entries"

        def lookups(self, request, model_admin):
                return (("deleted_only", "Only Deleted"),)

        def queryset(self, request, queryset):
            if self.value():
                return queryset.model.history.filter(history_type="-").distinct()
            return queryset

    def get_changelist(self, request, **kwargs):
        def url_from_result_maker(history=False):
            def custom_url_for_result(self, result):
                pk = getattr(result, self.pk_attname)
                route_type = 'history' if history else 'change'
                route = f'{self.opts.app_label}_{self.opts.model_name}_{route_type}'
                return reverse(f'admin:{route}',
                               args=(quote(pk),),
                               current_app=self.model_admin.admin_site.name)
            return custom_url_for_result

        changelist = super().get_changelist(request, **kwargs)
        if request.GET.get('entries', None) == 'deleted_only':
            changelist.url_for_result = url_from_result_maker(history=True)
        else:
            changelist.url_for_result = url_from_result_maker(history=False)
        return changelist

    def get_list_filter(self, request):
        return [self.SimpleHistoryShowDeletedFilter] + [
            f for f in super().get_list_filter(request)
        ]
