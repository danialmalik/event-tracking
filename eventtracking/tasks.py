import logging
from importlib import import_module

from celery import task
from eventtracking.utils import BackendJSONDecoder

LOG = logging.getLogger(__name__)


@task(name='eventtracking.async_routing')
def send_task_to_backend(backend_name, serialized_backend, event):

    try:
        backend = BackendJSONDecoder().default(serialized_backend)
    except (ValueError, AttributeError, TypeError, ImportError):
        raise ValueError('Cannot initialize backend %s' % backend_name)

    try:
        # TODO: initialize backend
        backend.send(event)
    except Exception:  # pylint: disable=broad-except
        LOG.exception(
            'Unable to send event to backend: %s', backend_module_path
        )
