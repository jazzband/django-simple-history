from __future__ import unicode_literals

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin
from .models import Poll, Choice, Person, Book, Document, Paper, Employee


class PersonAdmin(SimpleHistoryAdmin):
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Poll, SimpleHistoryAdmin)
admin.site.register(Choice, SimpleHistoryAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(Document, SimpleHistoryAdmin)
admin.site.register(Paper, SimpleHistoryAdmin)
admin.site.register(Employee, SimpleHistoryAdmin)
