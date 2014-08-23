from django.contrib.admin.sites import AdminSite
from simple_history.admin import SimpleHistoryAdmin
from .models import State

site = AdminSite(name="other_admin")

site.register(State, SimpleHistoryAdmin)
