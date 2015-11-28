from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from . import other_admin
from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^other-admin/', include(other_admin.site.urls)),

    url(r'^poll-list/$', views.PollListView.as_view(), name='poll_list'),

    url(r'^poll-history-versions-with-detail/(?P<pk>\d+)/$',
        views.PollHistoryVersionsView.as_view(), name='poll_history_versions_with_detail'),

    url(r'^poll-history-versions-with-update/(?P<pk>\d+)/$',
        views.PollHistoryVersions2.as_view(), name='poll_history_versions_with_update'),

    url(r'^poll-revert-view/(?P<pk>\d+)/$',
        views.PollRevertView.as_view(), name='poll_revert_view'),

    url(r'^pollrevertviewwithnormalform/(?P<pk>\d+)/$',
        views.PollRevertViewWithNormalForm.as_view(), name='pollrevertviewwithnormalform'),

    url(r'^pollrevertviewwithreadonlyform/(?P<pk>\d+)/$',
        views.PollRevertViewWithReadOnlyForm.as_view(), name='pollrevertviewwithreadonlyform'),

    url(r'^pollrevertviewwithgeneratedbyfunctionreadonlypollrevertform/(?P<pk>\d+)/$',
        views.PollRevertViewWithGeneratedByFunctionReadOnlyPollRevertForm.as_view(),
        name='pollrevertviewwithgeneratedbyfunctionreadonlypollrevertform'),

    url(r'^place-list/$',
        views.PlaceListView.as_view(), name='place_list'),

    url(r'^placerevertviewwithmissinghistoryrecordsfieldexception/(?P<pk>\d+)/$',
        views.PlaceRevertViewWithMissingHistoryRecordsFieldException.as_view(),
        name='placerevertviewwithmissinghistoryrecordsfieldexception'),

]
