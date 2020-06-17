"""Route events to processors and backends"""

from collections import OrderedDict
import logging

from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.backends.routing import RoutingBackend
LOG = logging.getLogger(__name__)


class RealtimeEventsBackend(RoutingBackend):
    def __init__(self, backends=None, processors=None):
        super(RealtimeEventsBackend, self).__init__(backends=backends, processors=processors)

    def send(self, event):
        """
        Process the event using all registered processors and send it to all registered backends.

        Logs and swallows all `Exception`.
        """
        try:
            processed_event = self.process_event(event)
        except EventEmissionExit:
            return
        else:
            self.send_to_backends(processed_event)
