from .models import HistoricalRecords


class HistoryRequestMiddleware:
    """Expose request to HistoricalRecords.

    This middleware sets request as a local context/thread variable, making it
    available to the model-level utilities to allow tracking of the authenticated user
    making a change.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        HistoricalRecords.context.request = request
        try:
            response = self.get_response(request)
        except Exception:
            raise
        finally:
            del HistoricalRecords.context.request
        return response
