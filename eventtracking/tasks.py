"""
Celery tasks
"""

import json

from celery.utils.log import get_task_logger
from celery import task

from eventtracking.async_tracker import AsyncTracker


logger = get_task_logger(__name__)


@task(name='eventtracking.tasks.async_send')
def async_send(settings_name, json_event):
    """
    Send event to configured backends asynchronously.

    Load the settings with name `settings_name` and use those to initalize a
    new tracker backend with all configured backends initiliazed. Send the event
    to async tracker backend.

    Arguments:
        settings_name(str):    JSON encoded backend
        json_event(str):      JSON encoded event
    """
    event = json.loads(json_event)
    tracker = AsyncTracker(backends_settings_name=settings_name)

    tracker.send_to_backends(event)
    logger.info('Successfully sent event "%s" to AsyncTracker.', event['name'])