from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from simple_history.tests.models import BucketDataRegister2, Poll


class PollCreate(CreateView):
    model = Poll
    fields = ['question', 'pub_date']


class PollUpdate(UpdateView):
    model = Poll
    fields = ['question', 'pub_date']


class PollDelete(DeleteView):
    model = Poll
    success_url = reverse_lazy('poll-list')


class PollList(ListView):
    model = Poll
    fields = ['question', 'pub_date']


class PollDetail(DetailView):
    model = Poll
    fields = ['question', 'pub_date']


class BucketDataRegister2Create(CreateView):
    model = BucketDataRegister2
    fields = ['data']


class BucketDataRegister2Detail(DetailView):
    model = BucketDataRegister2
    fields = ['data']
