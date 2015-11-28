from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views import generic

from simple_history.views import (HistoryRecordListViewMixin,
                                  RevertFromHistoryRecordViewMixin)

from .forms import (GeneratedByFunctionReadOnlyPollRevertForm, PollRevertForm,
                    ReadOnlyPollRevertForm)
from .models import Place, Poll


class PollListView(generic.ListView):
    model = Poll


class PollHistoryVersionsView(HistoryRecordListViewMixin, generic.DetailView):
    model = Poll


class PollHistoryVersions2(HistoryRecordListViewMixin, generic.UpdateView):
    model = Poll
    success_url = reverse_lazy('poll_list')


class PollRevertView(RevertFromHistoryRecordViewMixin, generic.UpdateView):
    model = Poll
    fields = '__all__'
    success_url = reverse_lazy('poll_list')


class PollRevertViewWithNormalForm(RevertFromHistoryRecordViewMixin, generic.UpdateView):
    model = Poll
    form_class = PollRevertForm
    success_url = reverse_lazy('poll_list')


class PollRevertViewWithReadOnlyForm(RevertFromHistoryRecordViewMixin, generic.UpdateView):
    model = Poll
    form_class = ReadOnlyPollRevertForm
    success_url = reverse_lazy('poll_list')


class PollRevertViewWithGeneratedByFunctionReadOnlyPollRevertForm(RevertFromHistoryRecordViewMixin,
                                                                  generic.UpdateView):
    model = Poll
    form_class = GeneratedByFunctionReadOnlyPollRevertForm
    success_url = reverse_lazy('poll_list')


class PlaceListView(generic.ListView):
    model = Place


class PlaceRevertViewWithMissingHistoryRecordsFieldException(RevertFromHistoryRecordViewMixin,
                                                             generic.UpdateView):
    model = Place
    fields = '__all__'
    success_url = reverse_lazy('place_list')
