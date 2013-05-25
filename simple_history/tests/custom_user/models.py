from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass

admin.site.register(CustomUser, UserAdmin)
