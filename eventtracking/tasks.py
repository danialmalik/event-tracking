"""
Celery tasks
"""

import json

from celery.utils.log import get_task_logger
from celery import task

from eventtracking.django.models import RegExFilter
from eventtracking.django.django_tracker import DjangoTracker


logger = get_task_logger(__name__)


@task(name='eventtracking.tasks.async_send')
def async_send(settings_name, json_event):
    """
    Send event to configured backends asynchronously.

    Load the settings with name `settings_name` and use those to initalize a
    new tracker backend with all configured backends initiliazed.
    If the event is allowed to be processed by the filter for a backend, call
    that backend's send to process event asynchronously.

    Arguments:
        settings_name(str):    JSON encoded backend
        json_event(str):      JSON encoded event
    """
    event = json.loads(json_event)
    event_name = event.get('name')

    tracker = DjangoTracker(backends_settings_name=settings_name)

    for backend_name, backend in tracker.backends.items():
        regex_filter = RegExFilter.get_latest_enabled_filter(backend_name=backend_name)

        if not regex_filter:
            logger.warning('Regular Expression Filter does not have any enabled '
                           'configurations for backend "%s". Allowing the event "%s" to pass through.',
                           backend_name, event_name)

        elif not regex_filter.string_passes_test(event_name):
            logger.info(
                'Event "%s" is not allowed to be processed by backend "%s"',
                event_name, backend_name
            )
            return

        else:
            logger.info(
                'Event "%s" is allowed to be processed by backend "%s"',
                event_name, backend_name
            )

        backend.send(event)
