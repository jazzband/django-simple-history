from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)
