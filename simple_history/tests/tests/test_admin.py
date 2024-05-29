from datetime import datetime, timedelta
from unittest.mock import ANY, patch

import django
from django.contrib.admin import AdminSite
from django.contrib.admin.utils import quote
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.encoding import force_str

from simple_history.admin import SimpleHistoryAdmin
from simple_history.models import HistoricalRecords
from simple_history.template_utils import HistoricalRecordContextHelper
from simple_history.tests.external.models import ExternalModelWithCustomUserIdField
from simple_history.tests.tests.utils import (
    PermissionAction,
    middleware_override_settings,
)

from ..models import (
    Book,
    BucketData,
    BucketMember,
    Choice,
    ConcreteExternal,
    Employee,
    FileModel,
    Person,
    Place,
    Planet,
    Poll,
    PollWithManyToMany,
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
            f"{site}:{app}_{model}_history",
            args=[quote(obj.pk)],
        )


class AdminSiteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

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

    def test_history_list_contains_diff_changes(self):
        self.login()
        poll = Poll(question="why?", pub_date=today)
        poll._history_user = self.user
        poll.save()

        poll_history_url = get_history_url(poll)
        response = self.client.get(poll_history_url)
        self.assertContains(response, "Changes")
        # The poll hasn't had any of its fields changed after creation,
        # so these values should not be present
        self.assertNotContains(response, "Question:")
        self.assertNotContains(response, "why?")
        self.assertNotContains(response, "Date published:")

        poll.question = "how?"
        poll.save()
        response = self.client.get(poll_history_url)
        self.assertContains(response, "Question:")
        self.assertContains(response, "why?")
        self.assertContains(response, "how?")
        self.assertNotContains(response, "Date published:")

        poll.question = "when?"
        poll.pub_date = parse_datetime("2024-04-04 04:04:04")
        poll.save()
        response = self.client.get(poll_history_url)
        self.assertContains(response, "Question:")
        self.assertContains(response, "why?")
        self.assertContains(response, "how?")
        self.assertContains(response, "when?")
        self.assertContains(response, "Date published:")
        self.assertContains(response, "2021-01-01 10:00:00")
        self.assertContains(response, "2024-04-04 04:04:04")

    def test_history_list_contains_diff_changes_for_foreign_key_fields(self):
        self.login()
        poll1 = Poll.objects.create(question="why?", pub_date=today)
        poll1_pk = poll1.pk
        poll2 = Poll.objects.create(question="how?", pub_date=today)
        poll2_pk = poll2.pk
        choice = Choice(poll=poll1, votes=1)
        choice._history_user = self.user
        choice.save()
        choice_history_url = get_history_url(choice)

        # Before changing the poll:
        response = self.client.get(choice_history_url)
        self.assertNotContains(response, "Poll:")
        expected_old_poll = f"Poll object ({poll1_pk})"
        self.assertNotContains(response, expected_old_poll)
        expected_new_poll = f"Poll object ({poll2_pk})"
        self.assertNotContains(response, expected_new_poll)

        # After changing the poll:
        choice.poll = poll2
        choice.save()
        response = self.client.get(choice_history_url)
        self.assertContains(response, "Poll:")
        self.assertContains(response, expected_old_poll)
        self.assertContains(response, expected_new_poll)

        # After deleting all polls:
        Poll.objects.all().delete()
        response = self.client.get(choice_history_url)
        self.assertContains(response, "Poll:")
        self.assertContains(response, f"Deleted poll (pk={poll1_pk})")
        self.assertContains(response, f"Deleted poll (pk={poll2_pk})")

    @patch(
        # Test without the customization in PollWithManyToMany's admin class
        "simple_history.tests.admin.HistoricalPollWithManyToManyContextHelper",
        HistoricalRecordContextHelper,
    )
    def test_history_list_contains_diff_changes_for_m2m_fields(self):
        self.login()
        poll = PollWithManyToMany(question="why?", pub_date=today)
        poll._history_user = self.user
        poll.save()
        place1 = Place.objects.create(name="Here")
        place1_pk = place1.pk
        place2 = Place.objects.create(name="There")
        place2_pk = place2.pk
        poll_history_url = get_history_url(poll)

        # Before adding places:
        response = self.client.get(poll_history_url)
        self.assertNotContains(response, "Places:")
        expected_old_places = "[]"
        self.assertNotContains(response, expected_old_places)
        expected_new_places = (
            f"[Place object ({place1_pk}), Place object ({place2_pk})]"
        )
        self.assertNotContains(response, expected_new_places)

        # After adding places:
        poll.places.add(place1, place2)
        response = self.client.get(poll_history_url)
        self.assertContains(response, "Places:")
        self.assertContains(response, expected_old_places)
        self.assertContains(response, expected_new_places)

        # After deleting all places:
        Place.objects.all().delete()
        response = self.client.get(poll_history_url)
        self.assertContains(response, "Places:")
        self.assertContains(response, expected_old_places)
        expected_new_places = (
            f"[Deleted place (pk={place1_pk}), Deleted place (pk={place2_pk})]"
        )
        self.assertContains(response, expected_new_places)

    def test_history_list_doesnt_contain_too_long_diff_changes(self):
        self.login()

        def create_and_change_poll(*, initial_question, changed_question) -> Poll:
            poll = Poll(question=initial_question, pub_date=today)
            poll._history_user = self.user
            poll.save()
            poll.question = changed_question
            poll.save()
            return poll

        repeated_chars = (
            HistoricalRecordContextHelper.DEFAULT_MAX_DISPLAYED_DELTA_CHANGE_CHARS
        )

        # Number of characters right on the limit
        poll1 = create_and_change_poll(
            initial_question="A" * repeated_chars,
            changed_question="B" * repeated_chars,
        )
        response = self.client.get(get_history_url(poll1))
        self.assertContains(response, "Question:")
        self.assertContains(response, "A" * repeated_chars)
        self.assertContains(response, "B" * repeated_chars)

        # Number of characters just over the limit
        poll2 = create_and_change_poll(
            initial_question="A" * (repeated_chars + 1),
            changed_question="B" * (repeated_chars + 1),
        )
        response = self.client.get(get_history_url(poll2))
        self.assertContains(response, "Question:")
        self.assertContains(response, f"{'A' * 61}[35 chars]AAAAA")
        self.assertContains(response, f"{'B' * 61}[35 chars]BBBBB")

    def test_overriding__historical_record_context_helper__with_custom_m2m_string(self):
        self.login()

        place1 = Place.objects.create(name="Place 1")
        place2 = Place.objects.create(name="Place 2")
        place3 = Place.objects.create(name="Place 3")
        poll = PollWithManyToMany.objects.create(question="why?", pub_date=today)
        poll.places.add(place1, place2)
        poll.places.set([place3])

        response = self.client.get(get_history_url(poll))
        self.assertContains(response, "Places:")
        self.assertContains(response, "[]")
        self.assertContains(response, "[<b>Place 1</b>, <b>Place 2</b>]")
        self.assertContains(response, "[<b>Place 3</b>]")

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

        admin.response_change(request, poll)

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
            **admin_site.each_context(request),
            # Verify this is set for original object
            "log_entries": ANY,
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
            "history_url": f"/admin/tests/poll/{poll.id}/history/",
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_view_permission": admin.has_view_history_permission(request, poll),
            "has_change_permission": admin.has_change_history_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled(request, poll),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        # DEV: Remove this when support for Django 4.2 has been dropped
        if django.VERSION < (5, 0):
            del context["log_entries"]

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
            **admin_site.each_context(request),
            # Verify this is set for history object not poll object
            "log_entries": ANY,
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
            "history_url": f"/admin/tests/poll/{poll.pk}/history/",
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_view_permission": admin.has_view_history_permission(request, poll),
            "has_change_permission": admin.has_change_history_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled(request, poll),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        # DEV: Remove this when support for Django 4.2 has been dropped
        if django.VERSION < (5, 0):
            del context["log_entries"]

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
            **admin_site.each_context(request),
            # Verify this is set for history object not poll object
            "log_entries": ANY,
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
            "history_url": f"/admin/tests/poll/{poll.id}/history/",
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_view_permission": admin.has_view_history_permission(request, poll),
            "has_change_permission": admin.has_change_history_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled(request, poll),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        # DEV: Remove this when support for Django 4.2 has been dropped
        if django.VERSION < (5, 0):
            del context["log_entries"]

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
            **admin_site.each_context(request),
            # Verify this is set for history object
            "log_entries": ANY,
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
            "has_view_permission": admin.has_view_history_permission(request, obj),
            "has_change_permission": admin.has_change_history_permission(request, obj),
            "has_delete_permission": admin.has_delete_permission(request, obj),
            "revert_disabled": admin.revert_disabled(request, obj),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        # DEV: Remove this when support for Django 4.2 has been dropped
        if django.VERSION < (5, 0):
            del context["log_entries"]

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
            **admin_site.each_context(request),
            # Verify this is set for original object
            "log_entries": ANY,
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
            "history_url": f"/admin/tests/poll/{poll.id}/history/",
            "add": False,
            "change": True,
            "has_add_permission": admin.has_add_permission(request),
            "has_view_permission": admin.has_view_history_permission(request, poll),
            "has_change_permission": admin.has_change_history_permission(request, poll),
            "has_delete_permission": admin.has_delete_permission(request, poll),
            "revert_disabled": admin.revert_disabled(request, poll),
            "has_file_field": True,
            "has_absolute_url": False,
            "form_url": "",
            "opts": ANY,
            "content_type_id": ANY,
            "save_as": admin.save_as,
            "save_on_top": admin.save_on_top,
            "root_path": getattr(admin_site, "root_path", None),
        }
        # DEV: Remove this when support for Django 4.2 has been dropped
        if django.VERSION < (5, 0):
            del context["log_entries"]

        mock_render.assert_called_once_with(
            request, admin.object_history_form_template, context
        )

    def assert_history_view_response_contains(
        self, user=None, *, title_prefix: PermissionAction, choose_date: bool
    ):
        user = user or self.user
        user = User.objects.get(pk=user.pk)  # refresh perms cache
        self.login(user)
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet))
        self.assertEqual(response.status_code, 200)
        # `count=None` means at least once
        self.assertContains(
            response,
            "Change history: Sun",
            count=None if title_prefix == PermissionAction.CHANGE else 0,
        )
        self.assertContains(
            response,
            "View history: Sun",
            count=None if title_prefix == PermissionAction.VIEW else 0,
        )
        self.assertContains(response, "Choose a date", count=None if choose_date else 0)

    def test_history_view__title_suggests_revert_by_default(self):
        self.assert_history_view_response_contains(
            title_prefix=PermissionAction.CHANGE, choose_date=True
        )

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=False)
    def test_history_view__title_suggests_revert(self):
        self.assert_history_view_response_contains(
            title_prefix=PermissionAction.CHANGE, choose_date=True
        )

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_view__title_suggests_view_only(self):
        self.assert_history_view_response_contains(
            title_prefix=PermissionAction.VIEW, choose_date=False
        )

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
        self.assertNotContains(response, "Revert")
        self.assertContains(response, "View Planet")
        self.assertContains(response, "View Sun")

    def _test_history_view_response_text_with_revert_disabled(self, *, disabled):
        user = User.objects.create(username="astronomer", is_staff=True, is_active=True)
        user.user_permissions.add(
            Permission.objects.get(codename="view_planet"),
            Permission.objects.get(codename="view_historicalplanet"),
        )
        self.assert_history_view_response_contains(
            user, title_prefix=PermissionAction.VIEW, choose_date=False
        )

        user.user_permissions.clear()
        user.user_permissions.add(
            Permission.objects.get(codename="view_planet"),
            Permission.objects.get(codename="change_planet"),
        )
        self.assert_history_view_response_contains(
            user,
            title_prefix=PermissionAction.VIEW if disabled else PermissionAction.CHANGE,
            choose_date=not disabled,
        )

    @override_settings(SIMPLE_HISTORY_REVERT_DISABLED=True)
    def test_history_view_response_text__revert_disabled(self):
        self._test_history_view_response_text_with_revert_disabled(disabled=True)

    def test_history_view_response_text__revert_enabled(self):
        self._test_history_view_response_text_with_revert_disabled(disabled=False)

    @override_settings(SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS=True)
    def test_history_form_view__no_perms_enforce_history_permissions(self):
        user = User.objects.create(username="astronomer", is_staff=True, is_active=True)
        user = User.objects.get(pk=user.pk)  # refresh perms cache
        self.client.force_login(user)
        planet = Planet.objects.create(star="Sun")
        response = self.client.get(get_history_url(planet, 0))
        self.assertEqual(response.status_code, 403)

    @override_settings(SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS=True)
    def test_history_view__no_perms_enforce_history_permissions(self):
        user = User.objects.create(username="astronomer", is_staff=True, is_active=True)
        user = User.objects.get(pk=user.pk)  # refresh perms cache
        self.client.force_login(user)
        planet = Planet.objects.create(star="Sun")
        resp = self.client.get(get_history_url(planet))
        self.assertEqual(resp.status_code, 403)

    @override_settings(
        SIMPLE_HISTORY_REVERT_DISABLED=True,
        SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS=True,
    )
    def test_history_view__enforce_history_permissions_and_revert_enabled(self):
        user = User.objects.create(username="astronomer", is_staff=True, is_active=True)
        user.user_permissions.add(
            Permission.objects.get(codename="view_historicalplanet"),
        )
        self.assert_history_view_response_contains(
            user, title_prefix=PermissionAction.VIEW, choose_date=False
        )

    def _test_permission_combos_with_enforce_history_permissions(self, *, enforced):
        user = User.objects.create(username="astronomer", is_staff=True, is_active=True)

        def get_request(usr):
            usr = User.objects.get(pk=usr.pk)  # refresh perms cache
            req = RequestFactory().post("/")
            req.session = "session"
            req._messages = FallbackStorage(req)
            req.user = usr
            return req

        admin_site = AdminSite()
        admin = SimpleHistoryAdmin(Planet, admin_site)

        # no perms
        request = get_request(user)
        self.assertFalse(admin.has_view_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertFalse(admin.has_view_history_permission(request))
        self.assertFalse(admin.has_change_history_permission(request))

        # has concrete view/change only -> view_historical is false
        user.user_permissions.clear()
        user.user_permissions.add(
            Permission.objects.get(codename="view_planet"),
            Permission.objects.get(codename="change_planet"),
        )
        request = get_request(user)
        self.assertTrue(admin.has_view_permission(request))
        self.assertTrue(admin.has_change_permission(request))
        self.assertEqual(admin.has_view_history_permission(request), not enforced)
        self.assertEqual(admin.has_change_history_permission(request), not enforced)

        # has concrete view/change and historical change -> view_history is false
        user.user_permissions.clear()
        user.user_permissions.add(
            Permission.objects.get(codename="view_planet"),
            Permission.objects.get(codename="change_planet"),
            Permission.objects.get(codename="change_historicalplanet"),
        )
        request = get_request(user)
        self.assertTrue(admin.has_view_permission(request))
        self.assertTrue(admin.has_change_permission(request))
        self.assertEqual(admin.has_view_history_permission(request), not enforced)
        self.assertTrue(admin.has_change_history_permission(request))

        # has concrete view/change and historical view/change -> view_history is true
        user.user_permissions.clear()
        user.user_permissions.add(
            Permission.objects.get(codename="view_planet"),
            Permission.objects.get(codename="change_planet"),
            Permission.objects.get(codename="view_historicalplanet"),
            Permission.objects.get(codename="change_historicalplanet"),
        )
        request = get_request(user)
        self.assertTrue(admin.has_view_permission(request))
        self.assertTrue(admin.has_change_permission(request))
        self.assertTrue(admin.has_view_history_permission(request))
        self.assertTrue(admin.has_change_history_permission(request))

        # has historical view only -> view_history is true
        user.user_permissions.clear()
        user.user_permissions.add(
            Permission.objects.get(codename="view_historicalplanet"),
        )
        request = get_request(user)
        self.assertFalse(admin.has_view_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertEqual(admin.has_view_history_permission(request), enforced)
        self.assertFalse(admin.has_change_history_permission(request))

    @override_settings(SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS=True)
    def test_permission_combos__enforce_history_permissions(self):
        self._test_permission_combos_with_enforce_history_permissions(enforced=True)

    def test_permission_combos__default(self):
        self._test_permission_combos_with_enforce_history_permissions(enforced=False)
