from datetime import datetime, timedelta
from django.test import TestCase
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from .. import models


class AsOfTest(TestCase):
    model = models.Document

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
        document = models.Document.objects.create()
        document.delete()
        for doc_change in models.Document.history.all():
            doc_change.history_date = now
            doc_change.save()
        docs_as_of_tmw = models.Document.history.as_of(now + timedelta(days=1))
        self.assertFalse(list(docs_as_of_tmw))

    def test_multiple(self):
        document1 = models.Document.objects.create()
        document2 = models.Document.objects.create()
        historical = models.Document.history.as_of(
            datetime.now() + timedelta(days=1))
        self.assertEqual(list(historical), [document1, document2])
