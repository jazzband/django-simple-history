import django

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.test.utils import override_settings
# from django_webtest import WebTest
from mock import ANY, patch
from simple_history.admin import SimpleHistoryAdmin, USER_NATURAL_KEY
from simple_history.models import HistoricalRecords
from simple_history.tests.admin import PlanetAdmin

from ..models import Planet
from .test_admin import get_history_url

User = get_user_model()


@override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
class AdminSiteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def tearDown(self):
        try:
            del HistoricalRecords.thread.request
        except AttributeError:
            pass

    def login(self, user=None, superuser=None):
        user = user or self.user
        user.is_superuser = True if superuser is None else superuser
        user.is_active = True
        user.save()
        self.client.force_login(user)

    def reset_permissions(self):
        for permission in Permission.objects.all():
            self.user.user_permissions.remove(permission)

    def add_view_permission(self, model_name):
        if django.VERSION >= (2, 1):
            self.user.user_permissions.add(
                Permission.objects.get(codename="view_{}".format(model_name))
            )

    def add_historical_view_permission(self, model_name):
        if django.VERSION >= (2, 1):
            self.user.user_permissions.add(
                Permission.objects.get(codename="view_historical{}".format(model_name))
            )

    def add_change_permission(self, model_name):
        self.user.user_permissions.add(
            Permission.objects.get(codename="change_{}".format(model_name))
        )

    def add_historical_change_permission(self, model_name):
        self.user.user_permissions.add(
            Permission.objects.get(codename="change_historical{}".format(model_name))
        )

    def test_history_view(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user

        Planet.objects.create(star="Andromeda")
        Planet.objects.create(star="Ursa Major")
        planet = Planet.objects.create(star="S")
        planet.star = "Su"
        planet.save()
        planet.star = "Sun"
        planet.save()

        admin_site = AdminSite()
        admin = PlanetAdmin(Planet, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            admin.history_view(request, str(planet.id))

        content_type = ContentType.objects.get_by_natural_key(*USER_NATURAL_KEY)
        admin_user_view = "admin:%s_%s_change" % (
            content_type.app_label,
            content_type.model,
        )

        context = {
            # Verify this is set for original object
            "title": ANY,
            "action_list": ANY,
            "module_name": "Planets",
            "object": planet,
            "root_path": ANY,
            "app_label": ANY,
            "opts": ANY,
            "admin_user_view": admin_user_view,
            "history_list_display": getattr(admin, "history_list_display", []),
            "has_change_permission": admin.has_change_permission(request, planet),
            "has_revert_permission": admin.has_revert_permission(request, planet),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_template, context
        )

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__view_perms_enabled1(self):
        """Assert 403 without matching "view" perms.
        """
        self.login(superuser=False)
        self.add_historical_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.client.get(get_history_url(planet), status=403)
        self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__view_perms_enabled2(self):
        """Assert 403 without matching "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.client.get(get_history_url(planet), status=403)
        self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__view_perms_enabled3(self):
        """Assert 200 because has "change" and "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        if django.VERSION >= (2, 1):
            self.client.get(get_history_url(planet), status=200)
            self.client.get(get_history_url(planet, 0), status=200)
        else:
            self.client.get(get_history_url(planet), status=403)
            self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled1(self):
        """Assert 403 without matching "change" perms.
        """
        self.login(superuser=False)
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.client.get(get_history_url(planet), status=403)
        self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled2(self):
        """Assert 403 without matching "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.client.get(get_history_url(planet), status=403)
        self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled3(self):
        """Assert 200 because has "change" and "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_change_permission("planet")
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.client.get(get_history_url(planet), status=200)
        self.client.get(get_history_url(planet, 0), status=200)

    def test_history_view__view_perms_enabled_title(self):
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        if django.VERSION >= (2, 1):
            response = self.client.get(get_history_url(planet))
            self.assertContains(response, "View history")

            response = self.client.get(get_history_url(planet, 0), status=200)
            self.assertContains(response, "View Sun")
        else:
            self.client.get(get_history_url(planet), status=403)
            self.client.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=False)
    def test_history_view__revert_disabled(self):
        """Assert can revert if not disabled through settings.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        self.add_change_permission("planet")
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")

        response = self.client.get(get_history_url(planet), status=200)
        self.assertContains(response, "Change history")

        response = self.client.get(get_history_url(planet, 0), status=200)
        self.assertContains(response, "Revert Sun")

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_view__revert_disabled_but_superuser(self):
        """Assert can "revert" if superuser even though
        disabled through settings.
        """
        self.login(superuser=True)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        self.add_change_permission("planet")
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")

        response = self.client.get(get_history_url(planet), status=200)
        self.assertContains(response, "Change history")

        response = self.client.get(get_history_url(planet, 0), status=200)
        self.assertContains(response, "Revert Sun")

    @tag("1")
    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_view__revert_disabled_not_superuser(self):
        """Assert cannot "revert" even though has all perms.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        self.add_change_permission("planet")
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")

        response = self.client.get(get_history_url(planet), status=200)
        self.assertContains(response, "View history")

        response = self.client.get(get_history_url(planet, 0), status=200)
        self.assertContains(response, "View Sun")

    def test_history_view__missing_objects(self):
        self.login(superuser=True)
        planet = Planet.objects.create(star="Sun")
        historical_model = planet.history.model
        planet_pk = planet.pk
        planet.delete()
        planet.pk = planet_pk
        historical_model.objects.all().delete()
        self.client.get(get_history_url(planet), status=302)

    def test_pre_django_21_without_historical(self):
        if django.VERSION < (2, 1):
            self.login(superuser=False)
            request = RequestFactory().post("/")
            request.session = "session"
            request._messages = FallbackStorage(request)
            request.user = self.user
            admin_site = AdminSite()
            admin = SimpleHistoryAdmin(Planet, admin_site=admin_site)
            planet = Planet.objects.create(star="Alpha")

            self.add_change_permission("planet")

            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True):
                self.assertFalse(admin.has_historical_view_permission(request, planet))
                self.assertFalse(
                    admin.has_historical_change_permission(request, planet)
                )
                self.assertFalse(
                    admin.has_historical_view_or_change_permission(request, planet)
                )
            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=False):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )

    def test_pre_django_21_with_historical(self):
        if django.VERSION < (2, 1):
            self.login(superuser=False)
            request = RequestFactory().post("/")
            request.session = "session"
            request._messages = FallbackStorage(request)
            request.user = self.user
            admin_site = AdminSite()
            admin = SimpleHistoryAdmin(Planet, admin_site=admin_site)
            planet = Planet.objects.create(star="Alpha")

            self.add_change_permission("planet")
            self.add_historical_change_permission("planet")

            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )
            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=False):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )

    def test_django_21_with_historical(self):
        if django.VERSION >= (2, 1):
            self.login(superuser=False)
            request = RequestFactory().post("/")
            request.session = "session"
            request._messages = FallbackStorage(request)
            request.user = self.user
            admin_site = AdminSite()
            admin = SimpleHistoryAdmin(Planet, admin_site=admin_site)
            planet = Planet.objects.create(star="Alpha")

            self.add_view_permission("planet")
            self.add_change_permission("planet")
            self.add_historical_view_permission("planet")
            self.add_historical_change_permission("planet")

            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )
            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=False):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )

    def test_django_21_without_historical(self):
        if django.VERSION >= (2, 1):
            self.login(superuser=False)
            request = RequestFactory().post("/")
            request.session = "session"
            request._messages = FallbackStorage(request)
            request.user = self.user
            admin_site = AdminSite()
            admin = SimpleHistoryAdmin(Planet, admin_site=admin_site)
            planet = Planet.objects.create(star="Alpha")

            self.add_view_permission("planet")
            self.add_change_permission("planet")

            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True):
                self.assertFalse(
                    admin.has_historical_view_or_change_permission(request, planet)
                )
            with override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=False):
                self.assertTrue(
                    admin.has_historical_view_or_change_permission(request, planet)
                )
