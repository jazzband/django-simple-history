from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin

from simple_history.tests.view import (
    BucketDataRegister2Create,
    BucketDataRegister2Detail,
    PollCreate,
    PollDelete,
    PollDetail,
    PollList,
    PollUpdate
)
from . import other_admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^other-admin/', other_admin.site.urls),
    url(r'^bucket_data/add/$', BucketDataRegister2Create.as_view(),
        name='bucket_data-add'),
    url(r'^bucket_data/(?P<pk>[0-9]+)/$', BucketDataRegister2Detail.as_view(),
        name='bucket_data-detail'),
    url(r'^poll/add/$', PollCreate.as_view(), name='poll-add'),
    url(r'^poll/(?P<pk>[0-9]+)/$', PollUpdate.as_view(), name='poll-update'),
    url(r'^poll/(?P<pk>[0-9]+)/delete/$', PollDelete.as_view(),
        name='poll-delete'),
    url(r'^polls/(?P<pk>[0-9]+)/$', PollDetail.as_view(), name='poll-detail'),
    url(r'^polls/$', PollList.as_view(), name='poll-list')
]
