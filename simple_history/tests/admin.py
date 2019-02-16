from __future__ import unicode_literals

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .external.models import ExternalModelWithCustomUserIdField
from .models import (
    Book,
    Choice,
    ConcreteExternal,
    Document,
    Employee,
    FileModel,
    Paper,
    Person,
    Poll,
    Planet,
)


class PersonAdmin(SimpleHistoryAdmin):
    pass


class ChoiceAdmin(SimpleHistoryAdmin):
    history_list_display = ["votes"]


class FileModelAdmin(SimpleHistoryAdmin):
    def test_method(self, obj):
        return "test_method_value"

    history_list_display = ["title", "test_method"]


class PlantAdmin(SimpleHistoryAdmin):
    def test_method(self, obj):
        return "test_method_value"

    history_list_display = ["title", "test_method"]


admin.site.register(Poll, SimpleHistoryAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(Document, SimpleHistoryAdmin)
admin.site.register(Paper, SimpleHistoryAdmin)
admin.site.register(Employee, SimpleHistoryAdmin)
admin.site.register(ConcreteExternal, SimpleHistoryAdmin)
admin.site.register(ExternalModelWithCustomUserIdField, SimpleHistoryAdmin)
admin.site.register(FileModel, FileModelAdmin)
admin.site.register(Planet, PlantAdmin)
