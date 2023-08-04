from datetime import date

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from simple_history.tests.custom_user.models import CustomUser
from simple_history.tests.models import (
    BucketDataRegisterRequestUser,
    Poll,
    PollWithHistoricalIPAddress,
)
from simple_history.utils import bulk_create_with_history, bulk_update_with_history


class PollCreate(CreateView):
    model = Poll
    fields = ["question", "pub_date"]


class PollBulkCreateView(View):
    def post(self, request, *args, **kwargs):
        poll_info_list = [
            {"question": "1", "pub_date": date(2020, 1, 1)},
            {"question": "2", "pub_date": date(2020, 1, 2)},
        ]
        polls_to_create = [Poll(**poll_info) for poll_info in poll_info_list]
        bulk_create_with_history(polls_to_create, Poll)
        return HttpResponse(status=200)


class PollBulkCreateWithDefaultUserView(View):
    def post(self, request, *args, **kwargs):
        default_user = CustomUser.objects.create_superuser(
            "test_user", "test_user@example.com", "pass"
        )
        # Bulk create objects with history
        poll_info_list = [
            {"question": "1", "pub_date": date(2020, 1, 1)},
            {"question": "2", "pub_date": date(2020, 1, 2)},
        ]
        polls_to_create = [Poll(**poll_info) for poll_info in poll_info_list]
        bulk_create_with_history(polls_to_create, Poll, default_user=default_user)
        return HttpResponse(status=200)


class PollBulkUpdateView(View):
    def post(self, request, *args, **kwargs):
        polls = Poll.objects.order_by("pub_date")
        for i, poll in enumerate(polls):
            poll.question = str(i)

        bulk_update_with_history(polls, fields=["question"], model=Poll)
        return HttpResponse(status=201)


class PollBulkUpdateWithDefaultUserView(View):
    def post(self, request, *args, **kwargs):
        default_user = CustomUser.objects.create_superuser(
            "test_user", "test_user@example.com", "pass"
        )
        polls = Poll.objects.all()
        for i, poll in enumerate(polls):
            poll.question = str(i)

        bulk_update_with_history(
            polls, fields=["question"], model=Poll, default_user=default_user
        )
        return HttpResponse(status=201)


class PollWithHistoricalIPAddressCreate(CreateView):
    model = PollWithHistoricalIPAddress
    fields = ["question", "pub_date"]


class PollUpdate(UpdateView):
    model = Poll
    fields = ["question", "pub_date"]


class PollDelete(DeleteView):
    model = Poll
    success_url = reverse_lazy("poll-list")


class PollList(ListView):
    model = Poll
    fields = ["question", "pub_date"]


class PollDetail(DetailView):
    model = Poll
    fields = ["question", "pub_date"]


class BucketDataRegisterRequestUserCreate(CreateView):
    model = BucketDataRegisterRequestUser
    fields = ["data"]


class BucketDataRegisterRequestUserDetail(DetailView):
    model = BucketDataRegisterRequestUser
    fields = ["data"]


class MockableView(View):
    """This view exists to easily mock a response."""

    def get(self, request, *args, **kwargs):
        return HttpResponse(status=200)
