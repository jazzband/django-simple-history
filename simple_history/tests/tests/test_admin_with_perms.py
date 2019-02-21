import django

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django_webtest import WebTest
from mock import ANY, patch
from simple_history.models import HistoricalRecords
from simple_history.tests.admin import PlantAdmin

from ..models import Planet
from .test_admin import login, get_history_url
from simple_history.admin import SimpleHistoryAdmin

User = get_user_model()


@override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
class AdminSiteTest(WebTest):
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def tearDown(self):
        try:
            del HistoricalRecords.thread.request
        except AttributeError:
            pass

    def login(self, user=None, superuser=None):
        return login(self, user, superuser)

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
        admin = PlantAdmin(Planet, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            admin.history_view(request, str(planet.id))

        context = {
            # Verify this is set for original object
            "title": admin.history_view_title(request, planet),
            "action_list": ANY,
            "module_name": "Planets",
            "object": planet,
            "root_path": ANY,
            "app_label": ANY,
            "opts": ANY,
            "admin_user_view": admin.admin_user_view,
            "history_list_display": admin.get_history_list_display(),
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
        self.app.get(get_history_url(planet), status=403)
        self.app.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__view_perms_enabled2(self):
        """Assert 403 without matching "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.app.get(get_history_url(planet), status=403)
        self.app.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__view_perms_enabled3(self):
        """Assert 200 because has "change" and "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        if django.VERSION >= (2, 1):
            self.app.get(get_history_url(planet), status=200)
            self.app.get(get_history_url(planet, 0), status=200)
        else:
            self.app.get(get_history_url(planet), status=403)
            self.app.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled1(self):
        """Assert 403 without matching "change" perms.
        """
        self.login(superuser=False)
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.app.get(get_history_url(planet), status=403)
        self.app.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled2(self):
        """Assert 403 without matching "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.app.get(get_history_url(planet), status=403)
        self.app.get(get_history_url(planet, 0), status=403)

    @override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
    def test_history_view__change_perms_enabled3(self):
        """Assert 200 because has "change" and "historicalchange" perms.
        """
        self.login(superuser=False)
        self.add_change_permission("planet")
        self.add_historical_change_permission("planet")
        planet = Planet.objects.create(star="Sun")
        self.app.get(get_history_url(planet), status=200)
        self.app.get(get_history_url(planet, 0), status=200)

    def test_history_view__view_perms_enabled_title(self):
        self.login(superuser=False)
        self.add_view_permission("planet")
        self.add_historical_view_permission("planet")
        planet = Planet.objects.create(star="Sun")
        if django.VERSION >= (2, 1):
            response = self.app.get(get_history_url(planet))
            self.assertIn("View history", response.unicode_normal_body)

            response = self.app.get(get_history_url(planet, 0), status=200)
            self.assertIn("View Sun", response.unicode_normal_body)
        else:
            self.app.get(get_history_url(planet), status=403)
            self.app.get(get_history_url(planet, 0), status=403)

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

        response = self.app.get(get_history_url(planet), status=200)
        self.assertIn("Change history", response.unicode_normal_body)

        response = self.app.get(get_history_url(planet, 0), status=200)
        self.assertIn("Revert Sun", response.unicode_normal_body)

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

        response = self.app.get(get_history_url(planet), status=200)
        self.assertIn("Change history", response)

        response = self.app.get(get_history_url(planet, 0), status=200)
        self.assertIn("Revert Sun", response.unicode_normal_body)

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

        response = self.app.get(get_history_url(planet), status=200)
        self.assertIn("View history", response)

        response = self.app.get(get_history_url(planet, 0), status=200)
        self.assertIn("View Sun", response.unicode_normal_body)

    def test_history_view__missing_objects(self):
        self.login(superuser=True)
        planet = Planet.objects.create(star="Sun")
        historical_model = planet.history.model
        planet_pk = planet.pk
        planet.delete()
        planet.pk = planet_pk
        historical_model.objects.all().delete()
        self.app.get(get_history_url(planet), status=302)

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
