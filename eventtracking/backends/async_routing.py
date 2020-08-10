"""Route events to processors and backends"""

from __future__ import absolute_import

import json
import logging

from eventtracking.backends.routing import RoutingBackend
from eventtracking.backends.logger import DateTimeJSONEncoder
from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.tasks import async_send


LOG = logging.getLogger(__name__)


ASYNC_ROUTING_SETTINGS_NAME = 'ASYNC_ROUTING_BACKENDS'


class AsyncRoutingBackend(RoutingBackend):
    """
    Route events to configured backends asynchronously
    """

    def send(self, event):
        """
        Process the event using all registered processors and send it to all registered backends.

        Arguments:
            event (dict) :  Open edX generated analytics event
        """
        try:
            processed_event = self.process_event(event)
        except EventEmissionExit:
            return

        try:
            json_event = json.dumps(processed_event, cls=DateTimeJSONEncoder)
        except ValueError:
            LOG.exception(
                'JSONEncodeError: Unable to encode event:%s', processed_event
            )
            return

        async_send.delay(ASYNC_ROUTING_SETTINGS_NAME, json_event)
