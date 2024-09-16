from django.contrib import admin
from django.utils.safestring import SafeString, mark_safe

from simple_history.admin import SimpleHistoryAdmin
from simple_history.template_utils import HistoricalRecordContextHelper
from simple_history.tests.external.models import ExternalModelWithCustomUserIdField

from .models import (
    Book,
    Choice,
    ConcreteExternal,
    Document,
    Employee,
    FileModel,
    Paper,
    Person,
    Place,
    Planet,
    Poll,
    PollWithManyToMany,
)


class PersonAdmin(SimpleHistoryAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False


class ChoiceAdmin(SimpleHistoryAdmin):
    history_list_display = ["votes"]


class FileModelAdmin(SimpleHistoryAdmin):
    def test_method(self, obj):
        return "test_method_value"

    history_list_display = ["title", "test_method"]


class PlanetAdmin(SimpleHistoryAdmin):
    def test_method(self, obj):
        return "test_method_value"

    history_list_display = ["title", "test_method"]


class HistoricalPollWithManyToManyContextHelper(HistoricalRecordContextHelper):
    def prepare_delta_change_value(self, change, value):
        display_value = super().prepare_delta_change_value(change, value)
        if change.field == "places":
            assert isinstance(display_value, list)
            assert all(isinstance(place, Place) for place in display_value)

            places = sorted(display_value, key=lambda place: place.name)
            display_value = list(map(self.place_display, places))
        return display_value

    @staticmethod
    def place_display(place: Place) -> SafeString:
        return mark_safe(f"<b>{place.name}</b>")


class PollWithManyToManyAdmin(SimpleHistoryAdmin):
    def get_historical_record_context_helper(self, request, historical_record):
        return HistoricalPollWithManyToManyContextHelper(self.model, historical_record)


admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(ConcreteExternal, SimpleHistoryAdmin)
admin.site.register(Document, SimpleHistoryAdmin)
admin.site.register(Employee, SimpleHistoryAdmin)
admin.site.register(ExternalModelWithCustomUserIdField, SimpleHistoryAdmin)
admin.site.register(FileModel, FileModelAdmin)
admin.site.register(Paper, SimpleHistoryAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Planet, PlanetAdmin)
admin.site.register(Poll, SimpleHistoryAdmin)
admin.site.register(PollWithManyToMany, PollWithManyToManyAdmin)
