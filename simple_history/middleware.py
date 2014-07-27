from . models import HistoricalRecords


class HistoryRequestMiddleware(object):
    """Expose the request as a thread-friendly variable on the
    HistoricalRecords class.

    """

    def process_request(self, request):
        HistoricalRecords.thread.request = request
