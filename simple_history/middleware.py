from .models import HistoricalRecords


class HistoryRequestMiddleware:
    """Expose request to HistoricalRecords.

    This middleware sets request as a local thread variable, making it
    available to the model-level utilities to allow tracking of the
    authenticated user making a change.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        HistoricalRecords.thread.request = request

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        if hasattr(HistoricalRecords.thread, 'request'):
            del HistoricalRecords.thread.request

        return response
