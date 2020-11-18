from django.utils.deprecation import MiddlewareMixin

from .models import HistoricalRecords


class HistoryRequestMiddleware(MiddlewareMixin):
    """Expose request to HistoricalRecords.

    This middleware sets request as a local context/thread variable, making it
    available to the model-level utilities to allow tracking of the authenticated user
    making a change.
    """

    def process_request(self, request):
        HistoricalRecords.context.request = request

    def process_response(self, request, response):
        if hasattr(HistoricalRecords.context, "request"):
            del HistoricalRecords.context.request
        return response
