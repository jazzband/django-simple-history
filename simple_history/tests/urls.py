from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from . import other_admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^other-admin/', other_admin.site.urls),
]
