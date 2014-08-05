from . models import HistoricalRecords


class HistoryRequestMiddleware(object):
    """Expose request to HistoricalRecords.

    This middleware sets request as a local thread variable, making it
    available to the model-level utilities to allow tracking of the
    authenticated user making a change.
    """

    def process_request(self, request):
        HistoricalRecords.thread.request = request
