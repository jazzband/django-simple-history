from django.contrib import admin
from django.urls import path, re_path

from simple_history.tests.view import (
    BucketDataRegisterRequestUserCreate,
    BucketDataRegisterRequestUserDetail,
    PollBulkCreateView,
    PollBulkCreateWithDefaultUserView,
    PollBulkUpdateView,
    PollBulkUpdateWithDefaultUserView,
    PollCreate,
    PollDelete,
    PollDetail,
    PollList,
    PollUpdate,
    PollWithHistoricalIPAddressCreate,
)

from . import other_admin

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("other-admin/", other_admin.site.urls),
    path(
        "bucket_data/add/",
        BucketDataRegisterRequestUserCreate.as_view(),
        name="bucket_data-add",
    ),
    re_path(
        r"^bucket_data/(?P<pk>[0-9]+)/$",
        BucketDataRegisterRequestUserDetail.as_view(),
        name="bucket_data-detail",
    ),
    path("poll/add/", PollCreate.as_view(), name="poll-add"),
    path(
        "pollwithhistoricalipaddress/add",
        PollWithHistoricalIPAddressCreate.as_view(),
        name="pollip-add",
    ),
    re_path(r"^poll/(?P<pk>[0-9]+)/$", PollUpdate.as_view(), name="poll-update"),
    re_path(r"^poll/(?P<pk>[0-9]+)/delete/$", PollDelete.as_view(), name="poll-delete"),
    re_path(r"^polls/(?P<pk>[0-9]+)/$", PollDetail.as_view(), name="poll-detail"),
    path("polls/", PollList.as_view(), name="poll-list"),
    path("polls-bulk-create/", PollBulkCreateView.as_view(), name="poll-bulk-create"),
    path(
        "polls-bulk-create-default-user/",
        PollBulkCreateWithDefaultUserView.as_view(),
        name="poll-bulk-create-with-default-user",
    ),
    path("polls-bulk-update/", PollBulkUpdateView.as_view(), name="poll-bulk-update"),
    path(
        "polls-bulk-update-default-user/",
        PollBulkUpdateWithDefaultUserView.as_view(),
        name="poll-bulk-update-with-default-user",
    ),
]
