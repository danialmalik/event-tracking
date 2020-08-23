"""Route events to processors and backends"""
import json
import logging

from eventtracking.backends.routing import RoutingBackend
from eventtracking.backends.logger import DateTimeJSONEncoder
from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.tasks import send_event
from eventtracking.async_tracker import ASYNC_ROUTING_BACKENDS_SETTINGS_NAME


LOG = logging.getLogger(__name__)


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
            LOG.info('Successfully processed event "{}"'.format(event['name']))
            json_event = json.dumps(processed_event, cls=DateTimeJSONEncoder)

        except EventEmissionExit:
            LOG.info('[EventEmissionExit] Stopping further processing'
                     ' of event "{}"'.format(event['name']))
            return

        except ValueError:
            LOG.exception(
                'JSONEncodeError: Unable to encode event: {}'.format(processed_event)
            )
            return

        send_event.delay(ASYNC_ROUTING_BACKENDS_SETTINGS_NAME, json_event)
