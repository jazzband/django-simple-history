from datetime import datetime, timedelta

from django_webtest import WebTest
from django.test.utils import override_settings
from django import VERSION
from django.core.urlresolvers import reverse
from django.conf import settings

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django < 1.5
    from django.contrib.auth.models import User
try:
    from django.contrib.admin.utils import quote
except ImportError:  # Django < 1.7
    from django.contrib.admin.util import quote

from simple_history.models import HistoricalRecords
from ..models import Book, Person, Poll, State, Employee


today = datetime(2021, 1, 1, 10, 0)
tomorrow = today + timedelta(days=1)


def get_history_url(obj, history_index=None, site="admin"):
    try:
        app, model = obj._meta.app_label, obj._meta.module_name
    except AttributeError:
        app, model = obj._meta.app_label, obj._meta.model_name
    if history_index is not None:
        history = obj.history.order_by('history_id')[history_index]
        return reverse(
            "{site}:{app}_{model}_simple_history".format(
                site=site, app=app, model=model),
            args=[quote(obj.pk), quote(history.history_id)],
        )
    else:
        return reverse("{site}:{app}_{model}_history".format(
            site=site, app=app, model=model), args=[quote(obj.pk)])


class AdminSiteTest(WebTest):
    def setUp(self):
        self.user = User.objects.create_superuser('user_login',
                                                  'u@example.com', 'pass')

    def tearDown(self):
        try:
            del HistoricalRecords.thread.request
        except AttributeError:
            pass

    def login(self, user=None):
        if user is None:
            user = self.user
        form = self.app.get(reverse('admin:index')).maybe_follow().form
        form['username'] = user.username
        form['password'] = 'pass'
        return form.submit()

    def test_history_list(self):
        if VERSION >= (1, 5):
            try:
                module_name = self.user._meta.module_name
            except AttributeError:
                module_name = self.user._meta.model_name
            self.assertEqual(module_name, 'customuser')
        self.login()
        poll = Poll(question="why?", pub_date=today)
        poll._history_user = self.user
        poll.save()
        response = self.app.get(get_history_url(poll))
        self.assertIn(get_history_url(poll, 0), response.unicode_normal_body)
        self.assertIn("Poll object", response.unicode_normal_body)
        self.assertIn("Created", response.unicode_normal_body)
        self.assertIn(self.user.username, response.unicode_normal_body)

    def test_history_form_permission(self):
        self.login(self.user)
        person = Person.objects.create(name='Sandra Hale')
        self.app.get(get_history_url(person, 0), status=403)

    def test_invalid_history_form(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        response = self.app.get(get_history_url(poll, 0))
        response.form['question'] = ""
        response = response.form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required", response.unicode_normal_body)

    def test_history_form(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        poll.question = "how?"
        poll.save()

        # Make sure form for initial version is correct
        response = self.app.get(get_history_url(poll, 0))
        self.assertEqual(response.form['question'].value, "why?")
        self.assertEqual(response.form['pub_date_0'].value, "2021-01-01")
        self.assertEqual(response.form['pub_date_1'].value, "10:00:00")

        # Create new version based on original version
        response.form['question'] = "what?"
        response.form['pub_date_0'] = "2021-01-02"
        response = response.form.submit()
        self.assertEqual(response.status_code, 302)
        if VERSION < (1, 4, 0):
            self.assertTrue(response.headers['location']
                            .endswith(get_history_url(poll)))
        else:
            self.assertTrue(response.headers['location']
                            .endswith(reverse('admin:tests_poll_changelist')))

        # Ensure form for second version is correct
        response = self.app.get(get_history_url(poll, 1))
        self.assertEqual(response.form['question'].value, "how?")
        self.assertEqual(response.form['pub_date_0'].value, "2021-01-01")
        self.assertEqual(response.form['pub_date_1'].value, "10:00:00")

        # Ensure form for new third version is correct
        response = self.app.get(get_history_url(poll, 2))
        self.assertEqual(response.form['question'].value, "what?")
        self.assertEqual(response.form['pub_date_0'].value, "2021-01-02")
        self.assertEqual(response.form['pub_date_1'].value, "10:00:00")

        # Ensure current version of poll is correct
        poll = Poll.objects.get()
        self.assertEqual(poll.question, "what?")
        self.assertEqual(poll.pub_date, tomorrow)
        self.assertEqual([p.history_user for p in Poll.history.all()],
                         [self.user, None, None])

    def test_history_user_on_save_in_admin(self):
        self.login()

        # Ensure polls created via admin interface save correct user
        add_page = self.app.get(reverse('admin:tests_poll_add'))
        add_page.form['question'] = "new poll?"
        add_page.form['pub_date_0'] = "2012-01-01"
        add_page.form['pub_date_1'] = "10:00:00"
        changelist_page = add_page.form.submit().follow()
        self.assertEqual(Poll.history.get().history_user, self.user)

        # Ensure polls saved on edit page in admin interface save correct user
        change_page = changelist_page.click("Poll object")
        change_page.form.submit()
        self.assertEqual([p.history_user for p in Poll.history.all()],
                         [self.user, self.user])

    def test_underscore_in_pk(self):
        self.login()
        book = Book(isbn="9780147_513731")
        book._history_user = self.user
        book.save()
        response = self.app.get(get_history_url(book))
        self.assertIn(book.history.all()[0].revert_url(),
                      response.unicode_normal_body)

    def test_historical_user_no_setter(self):
        """Demonstrate admin error without `_historical_user` setter.
        (Issue #43)

        """
        self.login()
        add_page = self.app.get(reverse('admin:tests_document_add'))
        self.assertRaises(AttributeError, add_page.form.submit)

    def test_historical_user_with_setter(self):
        """Documented work-around for #43"""
        self.login()
        add_page = self.app.get(reverse('admin:tests_paper_add'))
        add_page.form.submit()

    def test_history_user_not_saved(self):
        self.login()
        poll = Poll.objects.create(question="why?", pub_date=today)
        historical_poll = poll.history.all()[0]
        self.assertIsNone(
            historical_poll.history_user,
            "No way to know of request, history_user should be unset.",
        )

    def test_middleware_saves_user(self):
        overridden_settings = {
            'MIDDLEWARE_CLASSES':
                settings.MIDDLEWARE_CLASSES
                + ['simple_history.middleware.HistoryRequestMiddleware'],
        }
        with override_settings(**overridden_settings):
            self.login()
            poll = Poll.objects.create(question="why?", pub_date=today)
            historical_poll = poll.history.all()[0]
            self.assertEqual(historical_poll.history_user, self.user,
                             "Middleware should make the request available to "
                             "retrieve history_user.")

    def test_middleware_anonymous_user(self):
        overridden_settings = {
            'MIDDLEWARE_CLASSES':
                settings.MIDDLEWARE_CLASSES
                + ['simple_history.middleware.HistoryRequestMiddleware'],
        }
        with override_settings(**overridden_settings):
            self.app.get(reverse('admin:index'))
            poll = Poll.objects.create(question="why?", pub_date=today)
            historical_poll = poll.history.all()[0]
            self.assertEqual(historical_poll.history_user, None,
                             "Middleware request user should be able to "
                             "be anonymous.")

    def test_other_admin(self):
        """Test non-default admin instances.

        Make sure non-default admin instances can resolve urls and
        render pages.
        """
        self.login()
        state = State.objects.create()
        history_url = get_history_url(state, site="other_admin")
        self.app.get(history_url)
        change_url = get_history_url(state, 0, site="other_admin")
        self.app.get(change_url)

    def test_deleteting_user(self):
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

    def test_missing_one_to_one(self):
        """A relation to a missing one-to-one model should still show history"""
        self.login()
        manager = Employee.objects.create()
        employee = Employee.objects.create(manager=manager)
        employee.manager = None
        employee.save()
        manager.delete()
        response = self.app.get(get_history_url(employee, 0))
        self.assertEqual(response.status_code, 200)
