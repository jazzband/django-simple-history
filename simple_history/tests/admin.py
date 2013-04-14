from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin
from .models import Poll, Choice


admin.site.register(Poll, SimpleHistoryAdmin)
admin.site.register(Choice, SimpleHistoryAdmin)
