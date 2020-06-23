import logging
from celery.utils.log import get_task_logger

from eventtracking.backends.routing import RoutingBackend

LOGGER = logging.getLogger(__name__)
LOGGER = get_task_logger(__name__)

class XApiBackend(RoutingBackend):
    def send(self, event):
        LOGGER.info('xAPI')
        LOGGER.info(event)
