"""Route events to processors and backends asynchronously"""

from collections import OrderedDict
import logging

from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.backends.routing import RoutingBackend
from eventtracking.tasks import send_task_to_backend
from eventtracking.utils import BackendJSONEncoder, fullname, BackendJSONDecoder

LOG = logging.getLogger(__name__)


class AsyncRoutingBackend(RoutingBackend):
    def __init__(self, backends=None, processors=None, async_backends=None, **kwargs):
        self.async_backends = OrderedDict()

        super(AsyncRoutingBackend, self).__init__(backends=backends, processors=processors)

        if async_backends is not None:
            for name in sorted(async_backends.keys()):
                self.register_async_backend(name, async_backends[name])

    def register_async_backend(self, name, backend):
        """
        Register a new backend that will be called for each processed event.

        Note that backends are called in the order that they are registered.
        """
        if not hasattr(backend, 'send') or not callable(backend.send):
            raise ValueError('Backend %s does not have a callable "send" method.' % backend.__class__.__name__)
        else:
            self.async_backends[name] = backend

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
            self.send_to_backends_async(processed_event)

    def send_to_backends_async(self, event):
        """
        Sends the event to all registered backends.

        Logs and swallows all `Exception`.
        """
        for name, backend in self.backends.iteritems():
            try:
                serialized_self = BackendJSONEncoder().default(self)
                serialized_backed = BackendJSONEncoder().default(backend)

                LOG.info(serialized_self)
                LOG.info(serialized_backed)

                send_task_to_backend.delay(name, serialized_backed, event)
            except Exception:  # pylint: disable=broad-except
                LOG.exception(
                    'Unable to send event to backend: %s', name
                )
