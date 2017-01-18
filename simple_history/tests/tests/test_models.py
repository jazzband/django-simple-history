from __future__ import unicode_literals

from datetime import datetime, timedelta
import unittest
import warnings

import django
from django.db import models
from django.db.models.fields.proxy import OrderWrt
from django.test import TestCase
from django.core.files.base import ContentFile

from simple_history.models import HistoricalRecords, convert_auto_field
from ..models import (
    AdminProfile, Bookcase, MultiOneToOne, Poll, Choice, Restaurant,
    Person, FileModel, Document, Book, HistoricalPoll, Library, State,
    AbstractBase, ConcreteAttr, ConcreteUtil, SelfFK, Temperature, WaterLevel,
    ExternalModel1, ExternalModel3, UnicodeVerboseName, HistoricalChoice,
    HistoricalState, HistoricalCustomFKError, Series, SeriesWork, PollInfo,
    Employee, Country, Province,
    City, Contact, ContactRegister,
)
from ..external.models import ExternalModel2, ExternalModel4

try:
    from django.apps import apps
except ImportError:  # Django < 1.7
    from django.db.models import get_model
else:
    get_model = apps.get_model
try:
    from unittest import skipUnless
except ImportError:
    from unittest2 import skipUnless
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # django 1.4 compatibility
    from django.contrib.auth.models import User

today = datetime(2021, 1, 1, 10, 0)
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


def get_fake_file(filename):
    fake_file = ContentFile('file data')
    fake_file.name = filename
    return fake_file


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
        self.assertDatetimesEqual(update_record.history_date, datetime.now())

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

    def test_save_without_historical_record_for_registered_model(self):
        model = ExternalModel3.objects.create(name='registered model')
        self.assertTrue(hasattr(model, 'save_without_historical_record'))

    def test_save_raises_exception(self):
        anthony = Person(name='Anthony Gillard')
        with self.assertRaises(RuntimeError):
            anthony.save_without_historical_record()
        self.assertFalse(hasattr(anthony, 'skip_history_when_saving'))
        self.assertEqual(Person.history.count(), 0)
        anthony.save()
        self.assertEqual(Person.history.count(), 1)

    def test_foreignkey_field(self):
        why_poll = Poll.objects.create(question="why?", pub_date=today)
        how_poll = Poll.objects.create(question="how?", pub_date=today)
        choice = Choice.objects.create(poll=why_poll, votes=0)
        choice.poll = how_poll
        choice.save()
        update_record, create_record = Choice.history.all()
        self.assertRecordValues(create_record, Choice, {
            'poll_id': why_poll.id,
            'votes': 0,
            'id': choice.id,
            'history_type': "+",
        })
        self.assertRecordValues(update_record, Choice, {
            'poll_id': how_poll.id,
            'votes': 0,
            'id': choice.id,
            'history_type': "~",
        })

    def test_foreignkey_still_allows_reverse_lookup_via_set_attribute(self):
        lib = Library.objects.create()
        state = State.objects.create(library=lib)
        self.assertTrue(hasattr(lib, 'state_set'))
        self.assertIsNone(state._meta.get_field('library').rel.related_name,
                          "the '+' shouldn't leak through to the original "
                          "model's field related_name")

    def test_file_field(self):
        model = FileModel.objects.create(file=get_fake_file('name'))
        self.assertEqual(model.file.name, 'files/name')
        model.file.delete()
        update_record, create_record = model.history.all()
        self.assertEqual(create_record.file, 'files/name')
        self.assertEqual(update_record.file, '')

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

    def test_specify_history_user(self):
        user1 = User.objects.create_user('user1', '1@example.com')
        user2 = User.objects.create_user('user2', '1@example.com')
        document = Document.objects.create(changed_by=user1)
        document.changed_by = user2
        document.save()
        document.changed_by = None
        document.save()
        self.assertEqual([d.history_user for d in document.history.all()],
                         [None, user2, user1])

    def test_specify_history_date_1(self):
        temperature = Temperature.objects.create(
            location="London",
            temperature=14,
            _history_date=today,
        )
        temperature.temperature = 16
        temperature._history_date = yesterday
        temperature.save()
        self.assertEqual([t.history_date for t in temperature.history.all()],
                         [today, yesterday])

    def test_specify_history_date_2(self):
        river = WaterLevel.objects.create(waters="Thames", level=2.5,
                                          date=today)
        river.level = 2.6
        river.date = yesterday
        river.save()
        for t in river.history.all():
            self.assertEqual(t.date, t.history_date)

    def test_non_default_primary_key_save(self):
        book1 = Book.objects.create(isbn='1-84356-028-1')
        book2 = Book.objects.create(isbn='1-84356-028-2')
        library = Library.objects.create(book=book1)
        library.book = book2
        library.save()
        library.book = None
        library.save()
        self.assertEqual([l.book_id for l in library.history.all()],
                         [None, book2.pk, book1.pk])

    def test_string_defined_foreign_key_save(self):
        library1 = Library.objects.create()
        library2 = Library.objects.create()
        state = State.objects.create(library=library1)
        state.library = library2
        state.save()
        state.library = None
        state.save()
        self.assertEqual([s.library_id for s in state.history.all()],
                         [None, library2.pk, library1.pk])

    def test_self_referential_foreign_key(self):
        model = SelfFK.objects.create()
        other = SelfFK.objects.create()
        model.fk = model
        model.save()
        model.fk = other
        model.save()
        self.assertEqual([m.fk_id for m in model.history.all()],
                         [other.id, model.id, None])

    def test_to_field_foreign_key_save(self):
        country = Country.objects.create(code='US')
        country2 = Country.objects.create(code='CA')
        province = Province.objects.create(country=country)
        province.country = country2
        province.save()
        self.assertEqual([c.country_id for c in province.history.all()],
                         [country2.code, country.code])

    def test_db_column_foreign_key_save(self):
        country = Country.objects.create(code='US')
        city = City.objects.create(country=country)
        country_field = City._meta.get_field('country')
        self.assertIn(getattr(country_field, 'db_column'),
                      str(city.history.all().query))

    def test_raw_save(self):
        document = Document()
        document.save_base(raw=True)
        self.assertEqual(document.history.count(), 0)
        document.save()
        self.assertRecordValues(document.history.get(), Document, {
            'changed_by_id': None,
            'id': document.id,
            'history_type': "~",
        })

    def test_unicode_verbose_name(self):
        instance = UnicodeVerboseName()
        instance.save()
        self.assertEqual('historical \u570b',
                         instance.history.all()[0]._meta.verbose_name)

    def test_user_can_set_verbose_name(self):
        b = Book(isbn='54321')
        b.save()
        self.assertEqual('dead trees', b.history.all()[0]._meta.verbose_name)

    def test_historical_verbose_name_follows_model_verbose_name(self):
        l = Library()
        l.save()
        self.assertEqual('historical quiet please',
                         l.history.get()._meta.verbose_name)

    def test_foreignkey_primarykey(self):
        """Test saving a tracked model with a `ForeignKey` primary key."""
        poll = Poll(pub_date=today)
        poll.save()
        poll_info = PollInfo(poll=poll)
        poll_info.save()


class CreateHistoryModelTests(unittest.TestCase):

    def test_create_history_model_with_one_to_one_field_to_integer_field(self):
        records = HistoricalRecords()
        records.module = AdminProfile.__module__
        try:
            records.create_history_model(AdminProfile)
        except:
            self.fail("SimpleHistory should handle foreign keys to one to one"
                      "fields to integer fields without throwing an exception")

    def test_create_history_model_with_one_to_one_field_to_char_field(self):
        records = HistoricalRecords()
        records.module = Bookcase.__module__
        try:
            records.create_history_model(Bookcase)
        except:
            self.fail("SimpleHistory should handle foreign keys to one to one"
                      "fields to char fields without throwing an exception.")

    def test_create_history_model_with_multiple_one_to_ones(self):
        records = HistoricalRecords()
        records.module = MultiOneToOne.__module__
        try:
            records.create_history_model(MultiOneToOne)
        except:
            self.fail("SimpleHistory should handle foreign keys to one to one"
                      "fields to one to one fields without throwing an "
                      "exception.")


class AppLabelTest(TestCase):
    def get_table_name(self, manager):
        return manager.model._meta.db_table

    def test_explicit_app_label(self):
        self.assertEqual(self.get_table_name(ExternalModel1.objects),
                         'external_externalmodel1')

        self.assertEqual(self.get_table_name(ExternalModel1.history),
                         'external_historicalexternalmodel1')

    def test_default_app_label(self):
        self.assertEqual(self.get_table_name(ExternalModel2.objects),
                         'external_externalmodel2')
        self.assertEqual(self.get_table_name(ExternalModel2.history),
                         'external_historicalexternalmodel2')

    def test_register_app_label(self):
        self.assertEqual(self.get_table_name(ExternalModel3.objects),
                         'tests_externalmodel3')
        self.assertEqual(self.get_table_name(ExternalModel3.histories),
                         'external_historicalexternalmodel3')
        self.assertEqual(self.get_table_name(ExternalModel4.objects),
                         'external_externalmodel4')
        self.assertEqual(self.get_table_name(ExternalModel4.histories),
                         'tests_historicalexternalmodel4')

    def test_get_model(self):
        self.assertEqual(get_model('external', 'ExternalModel1'),
                         ExternalModel1)
        self.assertEqual(get_model('external', 'HistoricalExternalModel1'),
                         ExternalModel1.history.model)

        self.assertEqual(get_model('external', 'ExternalModel2'),
                         ExternalModel2)
        self.assertEqual(get_model('external', 'HistoricalExternalModel2'),
                         ExternalModel2.history.model)

        self.assertEqual(get_model('tests', 'ExternalModel3'),
                         ExternalModel3)
        self.assertEqual(get_model('external', 'HistoricalExternalModel3'),
                         ExternalModel3.histories.model)

        self.assertEqual(get_model('external', 'ExternalModel4'),
                         ExternalModel4)
        self.assertEqual(get_model('tests', 'HistoricalExternalModel4'),
                         ExternalModel4.histories.model)


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

    def test_get_model(self):
        self.assertEqual(get_model('tests', 'poll'),
                         Poll)
        self.assertEqual(get_model('tests', 'historicalpoll'),
                         HistoricalPoll)

    def test_most_recent_on_model_class(self):
        Poll.objects.create(question="what's up?", pub_date=today)
        self.assertRaises(TypeError, Poll.history.most_recent)

    def test_most_recent_nonexistant(self):
        # Unsaved poll
        poll = Poll(question="what's up?", pub_date=today)
        self.assertRaises(Poll.DoesNotExist, poll.history.most_recent)
        # Deleted poll
        poll.save()
        poll.delete()
        self.assertRaises(Poll.DoesNotExist, poll.history.most_recent)

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

        def question_as_of(time):
            return poll.history.as_of(time).question

        self.assertEqual(question_as_of(times[0]), "why?")
        self.assertEqual(question_as_of(times[1]), "how's it going?")
        self.assertEqual(question_as_of(times[2]), "what's up?")

    def test_as_of_nonexistant(self):
        # Unsaved poll
        poll = Poll(question="what's up?", pub_date=today)
        time = datetime.now()
        self.assertRaises(Poll.DoesNotExist, poll.history.as_of, time)
        # Deleted poll
        poll.save()
        poll.delete()
        self.assertRaises(Poll.DoesNotExist, poll.history.as_of, time)

    def test_foreignkey_field(self):
        why_poll = Poll.objects.create(question="why?", pub_date=today)
        how_poll = Poll.objects.create(question="how?", pub_date=today)
        choice = Choice.objects.create(poll=why_poll, votes=0)
        choice.poll = how_poll
        choice.save()
        most_recent = choice.history.most_recent()
        self.assertEqual(most_recent.poll.pk, how_poll.pk)
        times = [r.history_date for r in choice.history.all()]

        def poll_as_of(time):
            return choice.history.as_of(time).poll

        self.assertEqual(poll_as_of(times[0]).pk, how_poll.pk)
        self.assertEqual(poll_as_of(times[1]).pk, why_poll.pk)

    def test_abstract_inheritance(self):
        for klass in (ConcreteAttr, ConcreteUtil):
            obj = klass.objects.create()
            obj.save()
            update_record, create_record = klass.history.all()
            self.assertTrue(isinstance(update_record, AbstractBase))
            self.assertTrue(isinstance(create_record, AbstractBase))

    def test_invalid_bases(self):
        invalid_bases = (AbstractBase, "InvalidBases")
        for bases in invalid_bases:
            self.assertRaises(TypeError, HistoricalRecords, bases=bases)

    def test_import_related(self):
        field_object = HistoricalChoice._meta.get_field('poll')
        try:
            related_model = field_object.rel.related_model
        except AttributeError:  # Django<1.8
            related_model = field_object.related.model
        self.assertEqual(related_model, HistoricalChoice)

    def test_string_related(self):
        field_object = HistoricalState._meta.get_field('library')
        try:
            related_model = field_object.rel.related_model
        except AttributeError:  # Django<1.8
            related_model = field_object.related.model
        self.assertEqual(related_model, HistoricalState)

    @skipUnless(django.get_version() >= "1.7", "Requires 1.7 migrations")
    def test_state_serialization_of_customfk(self):
        from django.db.migrations import state
        state.ModelState.from_model(HistoricalCustomFKError)


class TestConvertAutoField(TestCase):
    """Check what AutoFields get converted to."""

    def setUp(self):
        for field in Poll._meta.fields:
            if isinstance(field, models.AutoField):
                self.field = field
                break

    def test_relational(self):
        """Relational test

        Default Django ORM uses an integer-based auto field.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning,
                                    message='Overriding setting DATABASES ' +
                                            'can lead to unexpected behavior.')
            with self.settings(DATABASES={'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2'}}):
                assert convert_auto_field(self.field) == models.IntegerField

    def test_non_relational(self):
        """Non-relational test

        MongoDB uses a string-based auto field. We need to make sure
        the converted field type is string.
        """

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning,
                                    message='Overriding setting DATABASES ' +
                                            'can lead to unexpected behavior.')
            with self.settings(DATABASES={'default': {
                    'ENGINE': 'django_mongodb_engine'}}):
                assert convert_auto_field(self.field) == models.TextField


class TestOrderWrtField(TestCase):
    """Check behaviour of _order field added by Meta.order_with_respect_to.

    The Meta.order_with_respect_to option adds an OrderWrt field named
    "_order", where OrderWrt is a proxy class for an IntegerField that sets
    some default options.

    The simple_history strategy is:
    - Convert to a plain IntegerField in the historical record
    - When restoring a historical instance, add the old value.  This may
      result in duplicate ordering values and non-deterministic ordering.
    """

    def setUp(self):
        """Create works in published order."""
        s = self.series = Series.objects.create(
            name="The Chronicles of Narnia", author="C.S. Lewis")
        self.w_lion = s.works.create(
            title="The Lion, the Witch and the Wardrobe")
        self.w_caspian = s.works.create(title="Prince Caspian")
        self.w_voyage = s.works.create(title="The Voyage of the Dawn Treader")
        self.w_chair = s.works.create(title="The Silver Chair")
        self.w_horse = s.works.create(title="The Horse and His Boy")
        self.w_nephew = s.works.create(title="The Magician's Nephew")
        self.w_battle = s.works.create(title="The Last Battle")

    def test_order(self):
        """Confirm that works are ordered by creation."""
        order = self.series.get_serieswork_order()
        expected = [
            self.w_lion.pk,
            self.w_caspian.pk,
            self.w_voyage.pk,
            self.w_chair.pk,
            self.w_horse.pk,
            self.w_nephew.pk,
            self.w_battle.pk]
        self.assertSequenceEqual(order, expected)
        self.assertEqual(0, self.w_lion._order)
        self.assertEqual(1, self.w_caspian._order)
        self.assertEqual(2, self.w_voyage._order)
        self.assertEqual(3, self.w_chair._order)
        self.assertEqual(4, self.w_horse._order)
        self.assertEqual(5, self.w_nephew._order)
        self.assertEqual(6, self.w_battle._order)

    def test_order_field_in_historical_model(self):
        work_order_field = self.w_lion._meta.get_field('_order')
        self.assertEqual(type(work_order_field), OrderWrt)

        history = self.w_lion.history.all()[0]
        history_order_field = history._meta.get_field('_order')
        self.assertEqual(type(history_order_field), models.IntegerField)

    def test_history_object_has_order(self):
        history = self.w_lion.history.all()[0]
        self.assertEqual(self.w_lion._order, history.history_object._order)

    def test_restore_object_with_changed_order(self):
        # Change a title
        self.w_caspian.title = 'Prince Caspian: The Return to Narnia'
        self.w_caspian.save()
        self.assertEqual(2, len(self.w_caspian.history.all()))
        self.assertEqual(1, self.w_caspian._order)

        # Switch to internal chronological order
        chronological = [
            self.w_nephew.pk,
            self.w_lion.pk,
            self.w_horse.pk,
            self.w_caspian.pk,
            self.w_voyage.pk,
            self.w_chair.pk,
            self.w_battle.pk]
        self.series.set_serieswork_order(chronological)
        self.assertSequenceEqual(self.series.get_serieswork_order(),
                                 chronological)

        # This uses an update, not a save, so no new history is created
        w_caspian = SeriesWork.objects.get(id=self.w_caspian.id)
        self.assertEqual(2, len(w_caspian.history.all()))
        self.assertEqual(1, w_caspian.history.all()[0]._order)
        self.assertEqual(1, w_caspian.history.all()[1]._order)
        self.assertEqual(3, w_caspian._order)

        # Revert to first title, old order
        old = w_caspian.history.all()[1].history_object
        old.save()
        w_caspian = SeriesWork.objects.get(id=self.w_caspian.id)
        self.assertEqual(3, len(w_caspian.history.all()))
        self.assertEqual(1, w_caspian.history.all()[0]._order)
        self.assertEqual(1, w_caspian.history.all()[1]._order)
        self.assertEqual(1, w_caspian.history.all()[2]._order)
        self.assertEqual(1, w_caspian._order)  # The order changed
        w_lion = SeriesWork.objects.get(id=self.w_lion.id)
        self.assertEqual(1, w_lion._order)  # and is identical to another order

        # New order is non-deterministic around identical IDs
        series = Series.objects.get(id=self.series.id)
        order = series.get_serieswork_order()
        self.assertEqual(order[0], self.w_nephew.pk)
        self.assertTrue(order[1] in (self.w_lion.pk, self.w_caspian.pk))
        self.assertTrue(order[2] in (self.w_lion.pk, self.w_caspian.pk))
        self.assertEqual(order[3], self.w_horse.pk)
        self.assertEqual(order[4], self.w_voyage.pk)
        self.assertEqual(order[5], self.w_chair.pk)
        self.assertEqual(order[6], self.w_battle.pk)

    @skipUnless(django.get_version() >= "1.7", "Requires 1.7 migrations")
    def test_migrations_include_order(self):
        from django.db.migrations import state
        model_state = state.ModelState.from_model(SeriesWork.history.model)
        found = False
        for name, field in model_state.fields:
            if name == '_order':
                found = True
                self.assertEqual(type(field), models.IntegerField)
        assert found, '_order not in fields ' + repr(model_state.fields)


class TestLatest(TestCase):
    """"Test behavior of `latest()` without any field parameters"""

    def setUp(self):
        poll = Poll.objects.create(
            question="Does `latest()` work?", pub_date=yesterday)
        poll.pub_date = today
        poll.save()

    def write_history(self, new_attributes):
        poll_history = HistoricalPoll.objects.all()
        for historical_poll, new_values in zip(poll_history, new_attributes):
            for fieldname, value in new_values.items():
                setattr(historical_poll, fieldname, value)
            historical_poll.save()

    def test_ordered(self):
        self.write_history([
            {'pk': 1, 'history_date': yesterday},
            {'pk': 2, 'history_date': today},
        ])
        assert HistoricalPoll.objects.latest().pk == 2

    def test_jumbled(self):
        self.write_history([
            {'pk': 1, 'history_date': today},
            {'pk': 2, 'history_date': yesterday},
        ])
        assert HistoricalPoll.objects.latest().pk == 1

    def test_sameinstant(self):
        self.write_history([
            {'pk': 1, 'history_date': yesterday},
            {'pk': 2, 'history_date': yesterday},
        ])
        assert HistoricalPoll.objects.latest().pk == 1


class TestMissingOneToOne(TestCase):

    def setUp(self):
        self.manager1 = Employee.objects.create()
        self.manager2 = Employee.objects.create()
        self.employee = Employee.objects.create(manager=self.manager1)
        self.employee.manager = self.manager2
        self.employee.save()
        self.manager1.delete()

    def test_history_is_complete(self):
        historical_manager_ids = list(self.employee.history.order_by('pk')
                                      .values_list('manager_id', flat=True))
        self.assertEqual(historical_manager_ids, [1, 2])

    def test_restore_employee(self):
        historical = self.employee.history.order_by('pk')[0]
        original = historical.instance
        self.assertEqual(original.manager_id, 1)
        with self.assertRaises(Employee.DoesNotExist):
            original.manager


class CustomTableNameTest1(TestCase):

    @staticmethod
    def get_table_name(manager):
        return manager.model._meta.db_table

    def test_custom_table_name(self):
        self.assertEqual(
            self.get_table_name(Contact.history),
            'contacts_history',
        )

    def test_custom_table_name_from_register(self):
        self.assertEqual(
            self.get_table_name(ContactRegister.history),
            'contacts_register_history',
        )
