from django.utils.deprecation import MiddlewareMixin

from .models import HistoricalRecords


class HistoryRequestMiddleware(MiddlewareMixin):
    """Expose request to HistoricalRecords.

    This middleware sets request as a local thread variable, making it
    available to the model-level utilities to allow tracking of the
    authenticated user making a change.
    """

    def process_request(self, request):
        HistoricalRecords.thread.request = request

    def process_response(self, request, response):
        if hasattr(HistoricalRecords.thread, 'request'):
            del HistoricalRecords.thread.request
        return response
