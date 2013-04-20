from datetime import datetime, timedelta
from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Poll, Choice, Restaurant


today = datetime(2021, 1, 1, 10, 0)
tomorrow = today + timedelta(days=1)


class HistoricalRecordsTest(TestCase):

    def assertDatetimesEqual(self, time1, time2):
        self.assertAlmostEqual(time1, time2, delta=timedelta(seconds=2))

    def assertRecordValues(self, record, klass, values_dict):
        for key, value in values_dict.items():
            self.assertEqual(getattr(record, key), value)
        self.assertEqual(record.history_object.__class__, klass)
        for key, value in values_dict.items():
            if key != 'history_type':
                self.assertEqual(getattr(record.history_object, key), value)

    def test_create(self):
        p = Poll(question="what's up?", pub_date=today)
        p.save()
        record, = p.history.all()
        self.assertRecordValues(record, Poll, {
            'question': "what's up?",
            'pub_date': today,
            'id': p.id,
            'history_type': "+"
        })
        self.assertDatetimesEqual(record.history_date, datetime.now())

    def test_update(self):
        Poll.objects.create(question="what's up?", pub_date=today)
        p = Poll.objects.get()
        p.pub_date = tomorrow
        p.save()
        update_record, create_record = p.history.all()
        self.assertRecordValues(create_record, Poll, {
            'question': "what's up?",
            'pub_date': today,
            'id': p.id,
            'history_type': "+"
        })
        self.assertRecordValues(update_record, Poll, {
            'question': "what's up?",
            'pub_date': tomorrow,
            'id': p.id,
            'history_type': "~"
        })

    def test_delete(self):
        p = Poll.objects.create(question="what's up?", pub_date=today)
        poll_id = p.id
        p.delete()
        delete_record, create_record = Poll.history.all()
        self.assertRecordValues(create_record, Poll, {
            'question': "what's up?",
            'pub_date': today,
            'id': poll_id,
            'history_type': "+"
        })
        self.assertRecordValues(delete_record, Poll, {
            'question': "what's up?",
            'pub_date': today,
            'id': poll_id,
            'history_type': "-"
        })

    def test_save_without_historical_record(self):
        pizza_place = Restaurant.objects.create(name='Pizza Place', rating=3)
        pizza_place.rating = 4
        pizza_place.save_without_historical_record()
        pizza_place.rating = 6
        pizza_place.save()
        update_record, create_record = Restaurant.updates.all()
        self.assertRecordValues(create_record, Restaurant, {
            'name': "Pizza Place",
            'rating': 3,
            'id': pizza_place.id,
            'history_type': "+",
        })
        self.assertRecordValues(update_record, Restaurant, {
            'name': "Pizza Place",
            'rating': 6,
            'id': pizza_place.id,
            'history_type': "~",
        })

    def test_inheritance(self):
        pizza_place = Restaurant.objects.create(name='Pizza Place', rating=3)
        pizza_place.rating = 4
        pizza_place.save()
        update_record, create_record = Restaurant.updates.all()
        self.assertRecordValues(create_record, Restaurant, {
            'name': "Pizza Place",
            'rating': 3,
            'id': pizza_place.id,
            'history_type': "+",
        })
        self.assertRecordValues(update_record, Restaurant, {
            'name': "Pizza Place",
            'rating': 4,
            'id': pizza_place.id,
            'history_type': "~",
        })


class RegisterTest(TestCase):
    def test_register_no_args(self):
        self.assertEqual(len(Choice.history.all()), 0)
        poll = Poll.objects.create(pub_date=today)
        choice = Choice.objects.create(poll=poll, votes=0)
        self.assertEqual(len(choice.history.all()), 1)

    def test_register_separate_app(self):
        get_history = lambda model: model.history
        self.assertRaises(AttributeError, get_history, User)
        self.assertEqual(len(User.histories.all()), 0)
        user = User.objects.create(username='bob', password='pass')
        self.assertEqual(len(User.histories.all()), 1)
        self.assertEqual(len(user.histories.all()), 1)


class HistoryManagerTest(TestCase):
    def test_most_recent(self):
        poll = Poll.objects.create(question="what's up?", pub_date=today)
        poll.question = "how's it going?"
        poll.save()
        poll.question = "why?"
        poll.save()
        poll.question = "how?"
        most_recent = poll.history.most_recent()
        self.assertEqual(most_recent.__class__, Poll)
        self.assertEqual(most_recent.question, "why?")

    def test_as_of(self):
        poll = Poll.objects.create(question="what's up?", pub_date=today)
        poll.question = "how's it going?"
        poll.save()
        poll.question = "why?"
        poll.save()
        poll.question = "how?"
        most_recent = poll.history.most_recent()
        self.assertEqual(most_recent.question, "why?")
        times = [r.history_date for r in poll.history.all()]
        question_as_of = lambda time: poll.history.as_of(time).question
        self.assertEqual(question_as_of(times[0]), "why?")
        self.assertEqual(question_as_of(times[1]), "how's it going?")
        self.assertEqual(question_as_of(times[2]), "what's up?")


def get_history_url(model, history_index=None):
    info = model._meta.app_label, model._meta.module_name
    if history_index is not None:
        history = model.history.order_by('history_id')[history_index]
        return reverse('admin:%s_%s_simple_history' % info,
            args=[model.pk, history.history_id])
    else:
        return reverse('admin:%s_%s_history' % info, args=[model.pk])


class AdminSiteTest(WebTest):
    def setUp(self):
        self.user = User.objects.create_superuser('u', 'u@example.com', 'pass')

    def login(self, username, password):
        form = self.app.get(reverse('admin:index')).form
        form['username'] = username
        form['password'] = password
        return form.submit()

    def test_history_list(self):
        self.login(username='u', password='pass')
        poll = Poll.objects.create(question="why?", pub_date=today)
        response = self.app.get(get_history_url(poll))
        self.assertIn(get_history_url(poll, 0), response.content)
        self.assertIn("Poll object", response.content)
        self.assertIn("Created", response.content)

    def test_history_form(self):
        self.login(username='u', password='pass')
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
        self.assertTrue(response.headers['location']
                        .endswith(get_history_url(poll)))

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
