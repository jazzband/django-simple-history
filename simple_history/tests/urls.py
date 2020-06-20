from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin

from simple_history.tests.view import (
    BucketDataRegisterRequestUserCreate,
    BucketDataRegisterRequestUserDetail,
    PollCreate,
    PollDelete,
    PollDetail,
    PollList,
    PollUpdate,
    PollWithHistoricalIPAddressCreate,
    PollBulkCreateView,
    PollBulkCreateWithDefaultUserView,
    PollBulkUpdateView,
    PollBulkUpdateWithDefaultUserView,
)
from . import other_admin

admin.autodiscover()

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^other-admin/", other_admin.site.urls),
    url(
        r"^bucket_data/add/$",
        BucketDataRegisterRequestUserCreate.as_view(),
        name="bucket_data-add",
    ),
    url(
        r"^bucket_data/(?P<pk>[0-9]+)/$",
        BucketDataRegisterRequestUserDetail.as_view(),
        name="bucket_data-detail",
    ),
    url(r"^poll/add/$", PollCreate.as_view(), name="poll-add"),
    url(
        r"^pollwithhistoricalipaddress/add$",
        PollWithHistoricalIPAddressCreate.as_view(),
        name="pollip-add",
    ),
    url(r"^poll/(?P<pk>[0-9]+)/$", PollUpdate.as_view(), name="poll-update"),
    url(r"^poll/(?P<pk>[0-9]+)/delete/$", PollDelete.as_view(), name="poll-delete"),
    url(r"^polls/(?P<pk>[0-9]+)/$", PollDetail.as_view(), name="poll-detail"),
    url(r"^polls/$", PollList.as_view(), name="poll-list"),
    url(r"^polls-bulk-create/$", PollBulkCreateView.as_view(), name="poll-bulk-create"),
    url(
        r"^polls-bulk-create-default-user/$",
        PollBulkCreateWithDefaultUserView.as_view(),
        name="poll-bulk-create-with-default-user",
    ),
    url(r"^polls-bulk-update/$", PollBulkUpdateView.as_view(), name="poll-bulk-update"),
    url(
        r"^polls-bulk-update-default-user/$",
        PollBulkUpdateWithDefaultUserView.as_view(),
        name="poll-bulk-update-with-default-user",
    ),
]
