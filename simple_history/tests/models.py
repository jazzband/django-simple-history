from __future__ import unicode_literals

from django.db import models

from simple_history.models import HistoricalRecords
from simple_history import register

from .custom_user.models import CustomUser as User


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    history = HistoricalRecords()


class Temperature(models.Model):
    location = models.CharField(max_length=200)
    temperature = models.IntegerField()

    history = HistoricalRecords()
    __history_date = None

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value


class WaterLevel(models.Model):
    waters = models.CharField(max_length=200)
    level = models.IntegerField()
    date = models.DateTimeField()

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.date


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

register(Choice)


class Voter(models.Model):
    user = models.ForeignKey(User)
    choice = models.ForeignKey(Choice, related_name='voters')


class HistoricalRecordsVerbose(HistoricalRecords):
    def get_extra_fields(self, model, fields):
        def verbose_str(self):
            return '%s changed by %s as of %s' % (
                self.history_object, self.history_user, self.history_date)

        extra_fields = super(
            HistoricalRecordsVerbose, self).get_extra_fields(model, fields)
        extra_fields['__str__'] = verbose_str
        return extra_fields

register(Voter, records_class=HistoricalRecordsVerbose)


class Place(models.Model):
    name = models.CharField(max_length=100)


class Restaurant(Place):
    rating = models.IntegerField()

    updates = HistoricalRecords()


class Person(models.Model):
    name = models.CharField(max_length=100)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if hasattr(self, 'skip_history_when_saving'):
            raise RuntimeError('error while saving')
        else:
            super(Person, self).save(*args, **kwargs)


class FileModel(models.Model):
    file = models.FileField(upload_to='files')
    history = HistoricalRecords()


class Document(models.Model):
    changed_by = models.ForeignKey(User, null=True, blank=True)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by


class Paper(Document):
    history = HistoricalRecords()

    @Document._history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class Profile(User):
    date_of_birth = models.DateField()


class AdminProfile(models.Model):
    profile = models.ForeignKey(Profile)


class State(models.Model):
    library = models.ForeignKey('Library', null=True)
    history = HistoricalRecords()


class Book(models.Model):
    isbn = models.CharField(max_length=15, primary_key=True)
    history = HistoricalRecords(verbose_name='dead trees')


class HardbackBook(Book):
    price = models.FloatField()


class Bookcase(models.Model):
    books = models.ForeignKey(HardbackBook)


class Library(models.Model):
    book = models.ForeignKey(Book, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'quiet please'


class BaseModel(models.Model):
    pass


class FirstLevelInheritedModel(BaseModel):
    pass


class SecondLevelInheritedModel(FirstLevelInheritedModel):
    pass


class AbstractBase(models.Model):

    class Meta:
        abstract = True


class ConcreteAttr(AbstractBase):
    history = HistoricalRecords(bases=[AbstractBase])


class ConcreteUtil(AbstractBase):
    pass

register(ConcreteUtil, bases=[AbstractBase])


class MultiOneToOne(models.Model):
    fk = models.ForeignKey(SecondLevelInheritedModel)


class SelfFK(models.Model):
    fk = models.ForeignKey('self', null=True)
    history = HistoricalRecords()


register(User, app='simple_history.tests', manager_name='histories')


class ExternalModel1(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        app_label = 'external'


class ExternalModel3(models.Model):
    name = models.CharField(max_length=100)

register(ExternalModel3, app='simple_history.tests.external',
         manager_name='histories')


class UnicodeVerboseName(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        verbose_name = '\u570b'


class CustomFKError(models.Model):
    fk = models.ForeignKey(SecondLevelInheritedModel)
    history = HistoricalRecords()


class Series(models.Model):
    """A series of works, like a trilogy of books."""
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)


class SeriesWork(models.Model):
    series = models.ForeignKey('Series', related_name='works')
    title = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = 'series'


class PollInfo(models.Model):
    poll = models.ForeignKey(Poll, primary_key=True)
    history = HistoricalRecords()


class UserAccessorDefault(models.Model):
    pass


class UserAccessorOverride(models.Model):
    pass


class Employee(models.Model):
    manager = models.OneToOneField('Employee', null=True)
    history = HistoricalRecords()


class Country(models.Model):
    code = models.CharField(max_length=15, unique=True)


class Province(models.Model):
    country = models.ForeignKey(Country, to_field='code')
    history = HistoricalRecords()


class City(models.Model):
    country = models.ForeignKey(Country, db_column='countryCode')
    history = HistoricalRecords()


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)
    history = HistoricalRecords(table_name='contacts_history')


class ContactRegister(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)

register(ContactRegister, table_name='contacts_register_history')


###############################################################################
#
# Inheritance examples
#
###############################################################################

class TrackedAbstractBaseA(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class TrackedAbstractBaseB(models.Model):
    history_b = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class UntrackedAbstractBase(models.Model):

    class Meta:
        abstract = True


class TrackedConcreteBase(models.Model):
    history = HistoricalRecords(inherit=True)


class UntrackedConcreteBase(models.Model):
    pass


class TrackedWithAbstractBase(TrackedAbstractBaseA):
    pass


class TrackedWithConcreteBase(TrackedConcreteBase):
    pass


class InheritTracking1(TrackedAbstractBaseA, UntrackedConcreteBase):
    pass


class BaseInheritTracking2(TrackedAbstractBaseA):
    pass


class InheritTracking2(BaseInheritTracking2):
    pass


class BaseInheritTracking3(TrackedAbstractBaseA):
    pass


class InheritTracking3(BaseInheritTracking3):
    pass


class InheritTracking4(TrackedAbstractBaseA):
    pass
