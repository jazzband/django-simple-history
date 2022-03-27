import datetime
import uuid

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.urls import reverse

from simple_history import register
from simple_history.models import HistoricalRecords, HistoricForeignKey

from .custom_user.models import CustomUser as User
from .external.models import AbstractExternal, AbstractExternal2, AbstractExternal3

get_model = apps.get_model


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse("poll-detail", kwargs={"pk": self.pk})


class PollWithNonEditableField(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    modified = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()


class PollWithUniqueQuestion(models.Model):
    question = models.CharField(max_length=200, unique=True)
    pub_date = models.DateTimeField("date published")

    history = HistoricalRecords()


class PollWithExcludeFields(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    place = models.TextField(null=True)

    history = HistoricalRecords(excluded_fields=["pub_date"])


class PollWithExcludedFieldsWithDefaults(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    expiration_time = models.DateField(default=datetime.date(2030, 12, 12))
    place = models.TextField(null=True)
    min_questions = models.PositiveIntegerField(default=1)
    max_questions = models.PositiveIntegerField()

    history = HistoricalRecords(
        excluded_fields=[
            "pub_date",
            "expiration_time",
            "place",
            "min_questions",
            "max_questions",
        ]
    )


class PollWithExcludedFKField(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    place = models.ForeignKey("Place", on_delete=models.CASCADE)

    history = HistoricalRecords(excluded_fields=["place"])


class AlternativePollManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(id=1)


class PollWithAlternativeManager(models.Model):
    some_objects = AlternativePollManager()
    all_objects = models.Manager()

    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    history = HistoricalRecords()


class IPAddressHistoricalModel(models.Model):
    ip_address = models.GenericIPAddressField()

    class Meta:
        abstract = True


class PollWithHistoricalIPAddress(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    history = HistoricalRecords(bases=[IPAddressHistoricalModel])

    def get_absolute_url(self):
        return reverse("poll-detail", kwargs={"pk": self.pk})


class CustomAttrNameForeignKey(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        self.attr_name = kwargs.pop("attr_name", None)
        super().__init__(*args, **kwargs)

    def get_attname(self):
        return self.attr_name or super().get_attname()

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.attr_name:
            kwargs["attr_name"] = self.attr_name
        return name, path, args, kwargs


class ModelWithCustomAttrForeignKey(models.Model):
    poll = CustomAttrNameForeignKey(Poll, models.CASCADE, attr_name="custom_poll")
    history = HistoricalRecords()


class CustomAttrNameOneToOneField(models.OneToOneField):
    def __init__(self, *args, **kwargs):
        self.attr_name = kwargs.pop("attr_name", None)
        super().__init__(*args, **kwargs)

    def get_attname(self):
        return self.attr_name or super().get_attname()

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.attr_name:
            kwargs["attr_name"] = self.attr_name
        return name, path, args, kwargs


class ModelWithCustomAttrOneToOneField(models.Model):
    poll = CustomAttrNameOneToOneField(Poll, models.CASCADE, attr_name="custom_poll")
    history = HistoricalRecords(excluded_field_kwargs={"poll": {"attr_name"}})


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

    history = HistoricalRecords(cascade_delete_history=True)

    @property
    def _history_date(self):
        return self.date


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()


register(Choice)


class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="voters")

    def __str__(self):
        return "Voter object"


class HistoricalRecordsVerbose(HistoricalRecords):
    def get_extra_fields(self, model, fields):
        def verbose_str(self):
            return "{} changed by {} as of {}".format(
                self.history_object,
                self.history_user,
                self.history_date,
            )

        extra_fields = super().get_extra_fields(model, fields)
        extra_fields["__str__"] = verbose_str
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
        if hasattr(self, "skip_history_when_saving"):
            raise RuntimeError("error while saving")
        else:
            super().save(*args, **kwargs)


class FileModel(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="files")
    history = HistoricalRecords()


# Set SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD
setattr(settings, "SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD", True)


class CharFieldFileModel(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="files")
    history = HistoricalRecords()


# Clear SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD
delattr(settings, "SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD")


class Document(models.Model):
    changed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        try:
            return self.changed_by
        except User.DoesNotExist:
            return None


class Paper(Document):
    history = HistoricalRecords()

    @Document._history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class RankedDocument(Document):
    rank = models.IntegerField(default=50)

    history = HistoricalRecords()


class Profile(User):
    date_of_birth = models.DateField()


class AdminProfile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


class State(models.Model):
    library = models.ForeignKey("Library", on_delete=models.CASCADE, null=True)
    history = HistoricalRecords()


class Book(models.Model):
    isbn = models.CharField(max_length=15, primary_key=True)
    history = HistoricalRecords(
        verbose_name="dead trees", verbose_name_plural="dead trees plural"
    )


class HardbackBook(Book):
    price = models.FloatField()


class Bookcase(models.Model):
    books = models.ForeignKey(HardbackBook, on_delete=models.CASCADE)


class Library(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "quiet please"
        verbose_name_plural = "quiet please plural"


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
    fk = models.ForeignKey(SecondLevelInheritedModel, on_delete=models.CASCADE)


class SelfFK(models.Model):
    fk = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    history = HistoricalRecords()


register(User, app="simple_history.tests", manager_name="histories")


class ExternalModelWithAppLabel(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        app_label = "external"


class ExternalModelSpecifiedWithAppParam(models.Model):
    name = models.CharField(max_length=100)


register(
    ExternalModelSpecifiedWithAppParam,
    app="simple_history.tests.external",
    manager_name="histories",
)


class UnicodeVerboseName(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "\u570b"


class UnicodeVerboseNamePlural(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "\u570b"


class CustomFKError(models.Model):
    fk = models.ForeignKey(SecondLevelInheritedModel, on_delete=models.CASCADE)
    history = HistoricalRecords()


class Series(models.Model):
    """A series of works, like a trilogy of books."""

    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)


class SeriesWork(models.Model):
    series = models.ForeignKey("Series", on_delete=models.CASCADE, related_name="works")
    title = models.CharField(max_length=100)
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = "series"


class PollInfo(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE, primary_key=True)
    history = HistoricalRecords()


class UserAccessorDefault(models.Model):
    pass


class UserAccessorOverride(models.Model):
    pass


class Employee(models.Model):
    manager = models.OneToOneField("Employee", null=True, on_delete=models.CASCADE)
    history = HistoricalRecords()


class Country(models.Model):
    code = models.CharField(max_length=15, unique=True)


class Province(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, to_field="code")
    history = HistoricalRecords()


class City(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, db_column="countryCode"
    )
    history = HistoricalRecords()


class Planet(models.Model):
    star = models.CharField(max_length=30)
    history = HistoricalRecords()

    def __str__(self):
        return self.star

    class Meta:
        verbose_name = "Planet"


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)
    history = HistoricalRecords(table_name="contacts_history")


class ContactRegister(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)


register(ContactRegister, table_name="contacts_register_history")


class ModelWithHistoryInDifferentApp(models.Model):
    name = models.CharField(max_length=30)
    history = HistoricalRecords(app="external")


class ModelWithHistoryInDifferentDb(models.Model):
    name = models.CharField(max_length=30)
    history = HistoricalRecords()


class ModelWithHistoryUsingBaseModelDb(models.Model):
    name = models.CharField(max_length=30)
    history = HistoricalRecords(use_base_model_db=True)


class ModelWithFkToModelWithHistoryUsingBaseModelDb(models.Model):
    fk = models.ForeignKey(
        ModelWithHistoryUsingBaseModelDb, on_delete=models.CASCADE, null=True
    )
    history = HistoricalRecords(use_base_model_db=True)


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


class ConcreteExternal(AbstractExternal):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "tests"


class ConcreteExternal2(AbstractExternal):
    name = models.CharField(max_length=50)

    class Meta:
        pass  # Don't set app_label to test inherited module path


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


class BasePlace(models.Model):
    name = models.CharField(max_length=50)
    history = HistoricalRecords(inherit=True)


class InheritedRestaurant(BasePlace):
    serves_hot_dogs = models.BooleanField(default=False)


class BucketMember(models.Model):
    name = models.CharField(max_length=30)
    user = models.OneToOneField(
        User, related_name="bucket_member", on_delete=models.CASCADE
    )


class BucketData(models.Model):
    changed_by = models.ForeignKey(
        BucketMember, on_delete=models.SET_NULL, null=True, blank=True
    )
    history = HistoricalRecords(user_model=BucketMember)

    @property
    def _history_user(self):
        return self.changed_by


def get_bucket_member_changed_by(instance, **kwargs):
    try:
        return instance.changed_by
    except AttributeError:
        return None


class BucketDataRegisterChangedBy(models.Model):
    changed_by = models.ForeignKey(
        BucketMember, on_delete=models.SET_NULL, null=True, blank=True
    )


register(
    BucketDataRegisterChangedBy,
    user_model=BucketMember,
    get_user=get_bucket_member_changed_by,
)


def get_bucket_member_request_user(request, **kwargs):
    try:
        return request.user.bucket_member
    except AttributeError:
        return None


class BucketDataRegisterRequestUser(models.Model):
    data = models.CharField(max_length=30)

    def get_absolute_url(self):
        return reverse("bucket_data-detail", kwargs={"pk": self.pk})


register(
    BucketDataRegisterRequestUser,
    user_model=BucketMember,
    get_user=get_bucket_member_request_user,
)


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))


class UUIDRegisterModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


register(UUIDRegisterModel, history_id_field=models.UUIDField(default=uuid.uuid4))

# Set the SIMPLE_HISTORY_HISTORY_ID_USE_UUID
setattr(settings, "SIMPLE_HISTORY_HISTORY_ID_USE_UUID", True)


class UUIDDefaultModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    history = HistoricalRecords()


# Clear the SIMPLE_HISTORY_HISTORY_ID_USE_UUID
delattr(settings, "SIMPLE_HISTORY_HISTORY_ID_USE_UUID")

# Set the SIMPLE_HISTORY_HISTORY_CHANGE_REASON_FIELD
setattr(settings, "SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD", True)


class DefaultTextFieldChangeReasonModel(models.Model):
    greeting = models.CharField(max_length=100)
    history = HistoricalRecords()


# Clear the SIMPLE_HISTORY_HISTORY_CHANGE_REASON_FIELD
delattr(settings, "SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD")


class UserTextFieldChangeReasonModel(models.Model):
    greeting = models.CharField(max_length=100)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))


class CharFieldChangeReasonModel(models.Model):
    greeting = models.CharField(max_length=100)
    history = HistoricalRecords()


class CustomManagerNameModel(models.Model):
    name = models.CharField(max_length=15)
    log = HistoricalRecords()


#
# Following classes test the "custom_model_name" option
#


class OverrideModelNameAsString(models.Model):
    name = models.CharField(max_length=15, unique=True)
    history = HistoricalRecords(custom_model_name="MyHistoricalCustomNameModel")


class OverrideModelNameAsCallable(models.Model):
    name = models.CharField(max_length=15, unique=True)
    history = HistoricalRecords(custom_model_name=lambda x: f"Audit{x}")


class AbstractModelCallable1(models.Model):
    history = HistoricalRecords(inherit=True, custom_model_name=lambda x: f"Audit{x}")

    class Meta:
        abstract = True


class OverrideModelNameUsingBaseModel1(AbstractModelCallable1):
    name = models.CharField(max_length=15, unique=True)


class OverrideModelNameUsingExternalModel1(AbstractExternal2):
    name = models.CharField(max_length=15, unique=True)


class OverrideModelNameUsingExternalModel2(AbstractExternal3):
    name = models.CharField(max_length=15, unique=True)


class OverrideModelNameRegisterMethod1(models.Model):
    name = models.CharField(max_length=15, unique=True)


register(
    OverrideModelNameRegisterMethod1,
    custom_model_name="MyOverrideModelNameRegisterMethod1",
)


class OverrideModelNameRegisterMethod2(models.Model):
    name = models.CharField(max_length=15, unique=True)


class ForeignKeyToSelfModel(models.Model):
    fk_to_self = models.ForeignKey(
        "ForeignKeyToSelfModel", null=True, related_name="+", on_delete=models.CASCADE
    )
    fk_to_self_using_str = models.ForeignKey(
        "self", null=True, related_name="+", on_delete=models.CASCADE
    )
    history = HistoricalRecords()


class Street(models.Model):
    name = models.CharField(max_length=150)
    log = HistoricalRecords(related_name="history")


class ManyToManyModelOther(models.Model):
    name = models.CharField(max_length=15, unique=True)


class BulkCreateManyToManyModel(models.Model):
    name = models.CharField(max_length=15, unique=True)
    other = models.ManyToManyField(ManyToManyModelOther)
    history = HistoricalRecords()


class ModelWithExcludedManyToMany(models.Model):
    name = models.CharField(max_length=15, unique=True)
    other = models.ManyToManyField(ManyToManyModelOther)
    history = HistoricalRecords(excluded_fields=["other"])


class ModelWithSingleNoDBIndexUnique(models.Model):
    name = models.CharField(max_length=15, unique=True, db_index=True)
    name_keeps_index = models.CharField(max_length=15, unique=True, db_index=True)
    history = HistoricalRecords(no_db_index="name")


class ModelWithMultipleNoDBIndex(models.Model):
    name = models.CharField(max_length=15, db_index=True)
    name_keeps_index = models.CharField(max_length=15, db_index=True)
    fk = models.ForeignKey(
        "Library", on_delete=models.CASCADE, null=True, related_name="+"
    )
    fk_keeps_index = models.ForeignKey(
        "Library", on_delete=models.CASCADE, null=True, related_name="+"
    )
    history = HistoricalRecords(no_db_index=["name", "fk", "other"])


class TestOrganization(models.Model):
    name = models.CharField(max_length=15, unique=True)


class TestOrganizationWithHistory(models.Model):
    name = models.CharField(max_length=15, unique=True)
    history = HistoricalRecords()


class TestParticipantToHistoricOrganization(models.Model):
    """
    Non-historic table foreign key to historic table.

    In this case it should simply behave like ForeignKey because
    the origin model (this one) cannot be historic, so foreign key
    lookups are always "current".
    """

    name = models.CharField(max_length=15, unique=True)
    organization = HistoricForeignKey(
        TestOrganizationWithHistory, on_delete=CASCADE, related_name="participants"
    )


class TestHistoricParticipantToOrganization(models.Model):
    """
    Historic table foreign key to non-historic table.

    In this case it should simply behave like ForeignKey because
    the origin model (this one) can be historic but the target model
    is not, so foreign key lookups are always "current".
    """

    name = models.CharField(max_length=15, unique=True)
    organization = HistoricForeignKey(
        TestOrganization, on_delete=CASCADE, related_name="participants"
    )
    history = HistoricalRecords()


class TestHistoricParticipanToHistoricOrganization(models.Model):
    """
    Historic table foreign key to historic table.

    In this case as_of queries on the origin model (this one)
    or on the target model (the other one) will traverse the
    foreign key relationship honoring the timepoint of the
    original query.  This only happens when both tables involved
    are historic.

    NOTE: related_name has to be different than the one used in
          TestParticipantToHistoricOrganization as they are
          sharing the same target table.
    """

    name = models.CharField(max_length=15, unique=True)
    organization = HistoricForeignKey(
        TestOrganizationWithHistory,
        on_delete=CASCADE,
        related_name="historic_participants",
    )
    history = HistoricalRecords()
