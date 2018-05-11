from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin

from simple_history.tests.view import (
    PollCreate,
    PollDelete,
    PollDetail,
    PollList,
    PollUpdate,
    raise_exception
)
from . import other_admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^other-admin/', other_admin.site.urls),
    url(r'^poll/add/$', PollCreate.as_view(), name='poll-add'),
    url(r'^poll/(?P<pk>[0-9]+)/$', PollUpdate.as_view(), name='poll-update'),
    url(r'^poll/(?P<pk>[0-9]+)/delete/$', PollDelete.as_view(),
        name='poll-delete'),
    url(r'^polls/(?P<pk>[0-9]+)/$', PollDetail.as_view(), name='poll-detail'),
    url(r'^polls/$', PollList.as_view(), name='poll-list'),
    url(r'^raise-exception/$', raise_exception, name='raise-exception'),
]
