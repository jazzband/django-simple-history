from datetime import datetime, timedelta
from operator import attrgetter

from django.db import IntegrityError
from django.test import TestCase, skipUnlessDBFeature

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from ..models import Document, Poll


class AsOfTest(TestCase):
    model = Document

    def setUp(self):
        user = User.objects.create_user("tester", "tester@example.com")
        self.now = datetime.now()
        self.yesterday = self.now - timedelta(days=1)
        self.obj = self.model.objects.create()
        self.obj.changed_by = user
        self.obj.save()
        self.model.objects.all().delete()   # allows us to leave PK on instance
        self.delete_history, self.change_history, self.create_history = (
            self.model.history.all())
        self.create_history.history_date = self.now - timedelta(days=2)
        self.create_history.save()
        self.change_history.history_date = self.now - timedelta(days=1)
        self.change_history.save()
        self.delete_history.history_date = self.now
        self.delete_history.save()

    def test_created_after(self):
        """An object created after the 'as of' date should not be
        included.

        """
        as_of_list = list(
            self.model.history.as_of(self.now - timedelta(days=5)))
        self.assertFalse(as_of_list)

    def test_deleted_before(self):
        """An object deleted before the 'as of' date should not be
        included.

        """
        as_of_list = list(
            self.model.history.as_of(self.now + timedelta(days=1)))
        self.assertFalse(as_of_list)

    def test_deleted_after(self):
        """An object created before, but deleted after the 'as of'
        date should be included.

        """
        as_of_list = list(
            self.model.history.as_of(self.now - timedelta(days=1)))
        self.assertEqual(len(as_of_list), 1)
        self.assertEqual(as_of_list[0].pk, self.obj.pk)

    def test_modified(self):
        """An object modified before the 'as of' date should reflect
        the last version.

        """
        as_of_list = list(
            self.model.history.as_of(self.now - timedelta(days=1)))
        self.assertEqual(as_of_list[0].changed_by, self.obj.changed_by)


class AsOfAdditionalTestCase(TestCase):

    def test_create_and_delete(self):
        now = datetime.now()
        document = Document.objects.create()
        document.delete()
        for doc_change in Document.history.all():
            doc_change.history_date = now
            doc_change.save()
        docs_as_of_tmw = Document.history.as_of(now + timedelta(days=1))
        self.assertFalse(list(docs_as_of_tmw))

    def test_multiple(self):
        document1 = Document.objects.create()
        document2 = Document.objects.create()
        historical = Document.history.as_of(
            datetime.now() + timedelta(days=1))
        self.assertEqual(list(historical), [document1, document2])


class BulkHistoryCreateTestCase(TestCase):
    def setUp(self):
        self.data = [
            Poll(id=1, question='Question 1', pub_date=datetime.now()),
            Poll(id=2, question='Question 2', pub_date=datetime.now()),
            Poll(id=3, question='Question 3', pub_date=datetime.now()),
            Poll(id=4, question='Question 4', pub_date=datetime.now()),
        ]

    def test_simple_bulk_history_create(self):
        created = Poll.history.bulk_history_create(self.data)
        self.assertEqual(len(created), 4)
        self.assertQuerysetEqual(Poll.history.order_by('question'), [
            'Question 1', 'Question 2', 'Question 3', 'Question 4'
        ], attrgetter('question'))

        created = Poll.history.bulk_create([])
        self.assertEqual(created, [])
        self.assertEqual(Poll.history.count(), 4)

    def test_bulk_history_create_on_objs_without_ids(self):
        self.data = [
            Poll(question='Question 1', pub_date=datetime.now()),
            Poll(question='Question 2', pub_date=datetime.now()),
            Poll(question='Question 3', pub_date=datetime.now()),
            Poll(question='Question 4', pub_date=datetime.now()),
        ]

        with self.assertRaises(IntegrityError):
            Poll.history.bulk_history_create(self.data)

    def test_set_custom_history_date_on_first_obj(self):
        self.data[0]._history_date = datetime(2000, 1, 1)

        Poll.history.bulk_history_create(self.data)

        self.assertEqual(Poll.history.order_by('question')[0].history_date,
                         datetime(2000, 1, 1))

    def test_set_custom_history_user_on_first_obj(self):
        user = User.objects.create_user("tester", "tester@example.com")
        self.data[0]._history_user = user

        Poll.history.bulk_history_create(self.data)

        self.assertEqual(Poll.history.order_by('question')[0].history_user,
                         user)

    @skipUnlessDBFeature('has_bulk_insert')
    def test_efficiency(self):
        with self.assertNumQueries(1):
            Poll.history.bulk_history_create(self.data)
