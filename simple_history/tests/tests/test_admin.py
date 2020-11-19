from datetime import datetime, timedelta
from unittest.mock import ANY, patch

import django
from django.contrib.admin import AdminSite
from django.contrib.admin.utils import quote
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.encoding import force_str

from simple_history.admin import SimpleHistoryAdmin
from simple_history.models import HistoricalRecords
from simple_history.tests.external.models import ExternalModelWithCustomUserIdField
from simple_history.tests.tests.utils import middleware_override_settings

from ..models import (
    Book,
    BucketData,
    BucketMember,
    Choice,
    ConcreteExternal,
    Employee,
    FileModel,
    Person,
    Planet,
    Poll,
    State,
)

User = get_user_model()
today = datetime(2021, 1, 1, 10, 0)
tomorrow = today + timedelta(days=1)


def get_history_url(obj, history_index=None, site="admin"):
    app, model = obj._meta.app_label, obj._meta.model_name
    if history_index is not None:
        history = obj.history.order_by("history_id")[history_index]
        return reverse(
            "{site}:{app}_{model}_simple_history".format(
                site=site, app=app, model=model
            ),
            args=[quote(obj.pk), quote(history.history_id)],
        )
    else:
        return reverse(
            "{site}:{app}_{model}_history".format(site=site, app=app, model=model),
            args=[quote(obj.pk)],
        )


class AdminSiteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def tearDown(self):
        try:
            del HistoricalRecords.context.request
        except AttributeError:
            pass

    def login(self, user=None, superuser=None):
        user = user or self.user
        if superuser is not None:
            user.is_superuser = True if superuser is None else superuser
            user.is_active = True
            user.save()
        self.client.force_login(user)

    def test_history_list(self):
        model_name = self.user._meta.model_name
        self.assertEqual(model_name, "customuser")
        self.login()
        poll = Poll(question="why?", pub_date=today)
        poll._change_reason = "A random test reason"
        poll._history_user = self.user
        poll.save()

        response = self.client.get(get_history_url(poll))
        self.assertContains(response, get_history_url(poll, 0))
        self.assertContains(response, "Poll object")
        self.assertContains(response, "Created")
        self.assertContains(response, "Changed by")
        self.assertContains(response, "Change reason")
        self.assertContains(response, "A random test reason")
        self.assertContains(response, self.user.username)

    def test_history_list_custom_fields(self):
        model_name = self.user._meta.model_name
        self.assertEqual(model_name, "customuser")
        self.login()
        poll = Poll(question="why?", pub_date=today)
        poll._history_user = self.user
        poll.save()
        choice = Choice(poll=poll, choice="because", votes=12)
        choice._history_user = self.user
        choice.save()
        choice.votes = 15
        choice.save()
        response = self.client.get(get_history_url(choice))
        self.assertContains(response, get_history_url(choice, 0))
        self.assertContains(response, "Choice object")
        self.assertContains(response, "Created")
        self.assertContains(response, self.user.username)
        self.assertContains(response, "votes")
        self.assertContains(response, "12")
        self.assertContains(response, "15")

    def test_history_list_custom_admin_methods(self):
        model_name = self.user._meta.model_name
        self.assertEqual(model_name, "customuser")
        self.login()
        file_model = FileModel(title="Title 1")
        file_model._history_user = self.user
        file_model.save()
        file_model.title = "Title 2"
        file_model.save()
        response = self.client.get(get_history_url(file_model))
        self.assertContains(response, get_history_url(file_model, 0))
        self.assertContains(response, "FileModel object")
        self.assertContains(response, "Created")
        self.assertContains(response, self.user.username)
        self.assertContains(response, "test_method_value")
        self.assertContains(response, "Title 1")
        self.assertContains(response, "Title 2")

    def test_history_list_custom_user_id_field(self):
        instance = ExternalModelWithCustomUserIdField(name="random_name")
        instance._history_user = self.user
        instance.save()

        self.login()
        resp = self.client.get(get_history_url(instance))

        self.assertEqual(200, resp.status_code)

    def test_history_view_permission(self):
        self.login()
        person = Person.objects.create(name="Sandra Hale")

        resp = self.client.get(get_history_url(person))

        self.assertEqual(403, resp.status_code)

    def test_history_form_permission(self):
        self.login(self.user)
        person = Person.objects.create(name="Sandra Hale")

        resp = self.client.get(get_history_url(person, 0))

        self.assertEqual(403, resp.status_code)

    def test_invalid_history_form(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        response = self.client.post(get_history_url(poll, 0), data={"question": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")

    def test_history_form(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()

        # Make sure form for initial version is correct
        response = self.client.get(get_history_url(poll, 0))
        form = response.context.get("adminform").form
        self.assertEqual(form["question"].value(), "why?")
        self.assertEqual(form["pub_date"].value(), datetime(2021, 1, 1, 10, 0))

        # Create new version based on original version
        new_data = {
            "pub_date_0": "2021-01-02",
            "pub_date_1": "10:00:00",
            "question": "what?",
        }
        response = self.client.post(get_history_url(poll, 0), data=new_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse("admin:tests_poll_changelist")))

        # Ensure form for second version is correct
        response = self.client.get(get_history_url(poll, 1))
        form = response.context.get("adminform").form
        self.assertEqual(form["question"].value(), "how?")
        self.assertEqual(form["pub_date"].value(), datetime(2021, 1, 1, 10, 0))

        # Ensure form for new third version is correct
        response = self.client.get(get_history_url(poll, 2))
        form = response.context["adminform"].form
        self.assertEqual(form["question"].value(), "what?")
        self.assertEqual(form["pub_date"].value(), datetime(2021, 1, 2, 10, 0))

        # Ensure current version of poll is correct
        poll = Poll.objects.get()
        self.assertEqual(poll.question, "what?")
        self.assertEqual(poll.pub_date, tomorrow)
        self.assertEqual(
            [p.history_user for p in Poll.history.all()], [self.user, None, None]
        )

    def test_history_user_on_save_in_admin(self):
        self.login()

        # Ensure polls created via admin interface save correct user
        poll_data = {
            "question": "new poll?",
            "pub_date_0": "2012-01-01",
            "pub_date_1": "10:00:00",
        }
        self.client.post(reverse("admin:tests_poll_add"), data=poll_data)
        self.assertEqual(Poll.history.get().history_user, self.user)

        # Ensure polls saved on edit page in admin interface save correct user
        self.client.post(reverse("admin:tests_poll_add"), data=poll_data)
        self.assertEqual(
            [p.history_user for p in Poll.history.all()], [self.user, self.user]
        )

    def test_underscore_in_pk(self):
        self.login()
        book = Book(isbn="9780147_513731")
        book._history_user = self.user
        book.save()
        response = self.client.get(get_history_url(book))
        self.assertContains(response, book.history.all()[0].revert_url())

    def test_historical_user_no_setter(self):
        """Demonstrate admin error without `_historical_user` setter.
        (Issue #43)

        """
        self.login()
        with self.assertRaises(AttributeError):
            self.client.post(reverse("admin:tests_document_add"))

    def test_historical_user_with_setter(self):
        """Documented work-around for #43"""
        self.login()
        self.client.post(reverse("admin:tests_paper_add"))

    def test_history_user_not_saved(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        historical_poll = poll.history.all()[0]
        self.assertIsNone(
            historical_poll.history_user,
            "No way to know of request, history_user should be unset.",
        )

    @override_settings(**middleware_override_settings)
    def test_middleware_saves_user(self):
        self.login()
        self.client.post(
            reverse("admin:tests_book_add"), data={"isbn": "9780147_513731"}
        )
        book = Book.objects.get()
        historical_book = book.history.all()[0]

        self.assertEqual(
            historical_book.history_user,
            self.user,
            "Middleware should make the request available to " "retrieve history_user.",
        )

    @override_settings(**middleware_override_settings)
    def test_middleware_unsets_request(self):
        self.login()
        self.client.get(reverse("admin:tests_book_add"))
        self.assertFalse(hasattr(HistoricalRecords.context, "request"))

    @override_settings(**middleware_override_settings)
    def test_rolled_back_user_does_not_lead_to_foreign_key_error(self):
        # This test simulates the rollback of a user after a request (which
        # happens, e.g. in test cases), and verifies that subsequently
        # creating a new entry does not fail with a foreign key error.
        self.login()
        self.assertEqual(
            self.client.get(reverse("admin:tests_book_add")).status_code, 200
        )

        book = Book.objects.create(isbn="9780147_513731")

        historical_book = book.history.all()[0]

        self.assertIsNone(
            historical_book.history_user,
            "No way to know of request, history_user should be unset.",
        )

    @override_settings(**middleware_override_settings)
    def test_middleware_anonymous_user(self):
        self.client.get(reverse("admin:index"))
        poll = Poll.objects.create(question="why?", pub_date=today)
        historical_poll = poll.history.all()[0]
        self.assertEqual(
            historical_poll.history_user,
            None,
            "Middleware request user should be able to " "be anonymous.",
        )

    def test_other_admin(self):
        """Test non-default admin instances.

        Make sure non-default admin instances can resolve urls and
        render pages.
        """
        self.login()
        state = State.objects.create()
        history_url = get_history_url(state, site="other_admin")
        self.client.get(history_url)
        change_url = get_history_url(state, 0, site="other_admin")
        self.client.get(change_url)

    def test_deleting_user(self):
        """Test deletes of a user does not cascade delete the history"""
        self.login()
        poll = Poll(question="why?", pub_date=today)
        poll._history_user = self.user
        poll.save()

        historical_poll = poll.history.all()[0]
        self.assertEqual(historical_poll.history_user, self.user)

        self.user.delete()

        historical_poll = poll.history.all()[0]
        self.assertEqual(historical_poll.history_user, None)

    def test_deleteting_member(self):
        """Test deletes of a BucketMember doesn't cascade delete the history"""
        self.login()
        member = BucketMember.objects.create(name="member1", user=self.user)
        bucket_data = BucketData(changed_by=member)
        bucket_data.save()

        historical_poll = bucket_data.history.all()[0]
        self.assertEqual(historical_poll.history_user, member)

        member.delete()

        historical_poll = bucket_data.history.all()[0]
        self.assertEqual(historical_poll.history_user, None)

    def test_missing_one_to_one(self):
        """A relation to a missing one-to-one model should still show
        history"""
        self.login()
        manager = Employee.objects.create()
        employee = Employee.objects.create(manager=manager)
        employee.manager = None
        employee.save()
        manager.delete()
        response = self.client.get(get_history_url(employee, 0))
        self.assertEqual(response.status_code, 200)

    def test_history_deleted_instance(self):
        """Ensure history page can be retrieved even for deleted instances"""
        self.login()
        employee = Employee.objects.create()
        employee_pk = employee.pk
        employee.delete()
        employee.pk = employee_pk
        response = self.client.get(get_history_url(employee))
        self.assertEqual(response.status_code, 200)

    def test_response_change(self):
        """
        Test the response_change method that it works with a _change_history
        in the POST and settings.SIMPLE_HISTORY_EDIT set to True
        """
        request = RequestFactory().post("/")
        request.POST = {"_change_history": True}
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.path = "/awesome/url/"

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.SIMPLE_HISTORY_EDIT", True):
            response = admin.response_change(request, poll)

        self.assertEqual(response["Location"], "/awesome/url/")

    def test_response_change_change_history_setting_off(self):
        """
        Test the response_change method that it works with a _change_history
        in the POST and settings.SIMPLE_HISTORY_EDIT set to False
        """
        request = RequestFactory().post("/")
        request.POST = {"_change_history": True}
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.path = "/awesome/url/"
        request.user = self.user

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        response = admin.response_change(request, poll)

        with patch("simple_history.admin.admin.ModelAdmin.response_change") as m_admin:
            m_admin.return_value = "it was called"
            response = admin.response_change(request, poll)

        self.assertEqual(response, "it was called")

    def test_response_change_no_change_history(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.admin.ModelAdmin.response_change") as m_admin:
            m_admin.return_value = "it was called"
            response = admin.response_change(request, poll)

        self.assertEqual(response, "it was called")

    def test_history_form_view_without_getting_history(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()
        history = poll.history.all()[0]

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            admin.history_form_view(request, poll.id, history.pk)

        context = {
            # Verify this is set for original object
            "original": poll,
            "change_history": False,
            "title": "Revert %s" % force_str(poll),
            "adminform": ANY,
            "object_id": poll.id,
            "is_popup": False,
            "media": ANY,
            "errors": ANY,
            "app_label": "tests",
            "original_opts": ANY,
            "changelist_url": "/admin/tests/poll/",
            "change_url": ANY,
            "history_url": "/admin/tests/poll/{}/history/".format(poll.id),
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_change_permission": admin.has_change_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled,
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def test_history_form_view_getting_history(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user
        request.POST = {"_change_history": True}

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()
        history = poll.history.all()[0]

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            with patch("simple_history.admin.SIMPLE_HISTORY_EDIT", True):
                admin.history_form_view(request, poll.id, history.pk)

        context = {
            # Verify this is set for history object not poll object
            "original": history.instance,
            "change_history": True,
            "title": "Revert %s" % force_str(history.instance),
            "adminform": ANY,
            "object_id": poll.id,
            "is_popup": False,
            "media": ANY,
            "errors": ANY,
            "app_label": "tests",
            "original_opts": ANY,
            "changelist_url": "/admin/tests/poll/",
            "change_url": ANY,
            "history_url": "/admin/tests/poll/{pk}/history/".format(pk=poll.pk),
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_change_permission": admin.has_change_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled,
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def test_history_form_view_getting_history_with_setting_off(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user
        request.POST = {"_change_history": True}

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()
        history = poll.history.all()[0]

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            with patch("simple_history.admin.SIMPLE_HISTORY_EDIT", False):
                admin.history_form_view(request, poll.id, history.pk)

        context = {
            # Verify this is set for history object not poll object
            "original": poll,
            "change_history": False,
            "title": "Revert %s" % force_str(poll),
            "adminform": ANY,
            "object_id": poll.id,
            "is_popup": False,
            "media": ANY,
            "errors": ANY,
            "app_label": "tests",
            "original_opts": ANY,
            "changelist_url": "/admin/tests/poll/",
            "change_url": ANY,
            "history_url": "/admin/tests/poll/{}/history/".format(poll.id),
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_change_permission": admin.has_change_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled,
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def test_history_form_view_getting_history_abstract_external(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user
        request.POST = {"_change_history": True}

        obj = ConcreteExternal.objects.create(name="test")
        obj.name = "new_test"
        obj.save()
        history = obj.history.all()[0]

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(ConcreteExternal, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            with patch("simple_history.admin.SIMPLE_HISTORY_EDIT", True):
                admin.history_form_view(request, obj.id, history.pk)

        context = {
            # Verify this is set for history object
            "original": history.instance,
            "change_history": True,
            "title": "Revert %s" % force_str(history.instance),
            "adminform": ANY,
            "object_id": obj.id,
            "is_popup": False,
            "media": ANY,
            "errors": ANY,
            "app_label": "tests",
            "original_opts": ANY,
            "changelist_url": "/admin/tests/concreteexternal/",
            "change_url": ANY,
            "history_url": "/admin/tests/concreteexternal/{pk}/history/".format(
                pk=obj.pk
            ),
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_change_permission": admin.has_change_permission(request, obj),
            "has_delete_permission": admin.has_delete_permission(request, obj),
            "revert_disabled": admin.revert_disabled,
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def test_history_form_view_accepts_additional_context(self):
        request = RequestFactory().post("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.user = self.user

        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()
        history = poll.history.all()[0]

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Poll, admin_site)

        with patch("simple_history.admin.render") as mock_render:
            admin.history_form_view(
                request,
                poll.id,
                history.pk,
                extra_context={"anything_else": "will be merged into context"},
            )

        context = {
            # Verify this is set for original object
            "anything_else": "will be merged into context",
            "original": poll,
            "change_history": False,
            "title": "Revert %s" % force_str(poll),
            "adminform": ANY,
            "object_id": poll.id,
            "is_popup": False,
            "media": ANY,
            "errors": ANY,
            "app_label": "tests",
            "original_opts": ANY,
            "changelist_url": "/admin/tests/poll/",
            "change_url": ANY,
            "history_url": "/admin/tests/poll/{}/history/".format(poll.id),
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_change_permission": admin.has_change_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled,
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        context.update(admin_site.each_context(request))
        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def test_history_view__title_suggests_revert_by_default(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet))
        self.assertContains(response, "Change history: Sun")

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=False)
    def test_history_view__title_suggests_revert(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet))
        self.assertContains(response, "Change history: Sun")
        self.assertContains(response, "Choose a date")

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_view__title_suggests_view_only(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet))
        self.assertContains(response, "View history: Sun")
        self.assertNotContains(response, "Choose a date")

    def test_history_form_view__shows_revert_button_by_default(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet, 0))
        self.assertContains(response, "Revert Planet")
        self.assertContains(response, "Revert Sun")
        self.assertContains(response, "Press the 'Revert' button")

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=False)
    def test_history_form_view__shows_revert_button(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet, 0))
        self.assertContains(response, "Revert Planet")
        self.assertContains(response, "Revert Sun")
        self.assertContains(response, "Press the 'Revert' button")

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_form_view__does_not_show_revert_button(self):
        self.login()
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet, 0))
        self.assertContains(response, "View Planet")
        self.assertContains(response, "View Sun")
        self.assertNotContains(response, "Revert")
