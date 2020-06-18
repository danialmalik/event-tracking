import logging
import pickle

from pickle import UnpicklingError
from importlib import import_module
from celery.utils.log import get_task_logger

from celery import task

LOG = get_task_logger(__name__)


@task(name='eventtracking.async_routing')
def send_task_to_backend(backend_name, pickled_backend, event):

    try:
        backend = pickle.loads(pickled_backend)
    except UnpicklingError:
        raise ValueError('Cannot initialize backend %s' % backend_name)

    try:
        backend.send(event)
    except Exception:  # pylint: disable=broad-except
        LOG.exception(
            'Unable to send event to backend: %s', backend_name
        )
