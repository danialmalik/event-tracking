"""
Tracking backend for asynchronous routing.
"""
import re
from logging import getLogger
from collections import namedtuple

from django.conf import settings

from eventtracking.django.django_tracker import DjangoTracker
from eventtracking.exceptions import ImproperlyConfigured


ALLOWLIST = 'allowlist'
BLOCKLIST = 'blocklist'
ASYNC_ROUTING_BACKENDS_SETTINGS_NAME = 'ASYNC_ROUTING_BACKENDS'
ASYNC_ROUTING_FILTERS_SETTINGS_NAME = 'ASYNC_ROUTING_FILTERS'


logger = getLogger(__name__)
FilterConfig = namedtuple('FilterConfig', ['type', 'regular_expressions'])


class AsyncTracker(DjangoTracker):
    """
    Tracking backend for asynchronous routing.

    Contains utility methods for filtering the events.
    """

    def send_to_backends(self, event):
        """
        Send the event to all registered backends. Log and swallow all exceptions
        if raised.

        Arguments:
            event (dict)    :   analytics event dictionary
        """

        for name, backend in self.backends.items():
            try:
                if self.should_event_pass(event, name):
                    logger.info('Sending event "%s" to backend "%s"', event['name'], name)
                    backend.send(event)
                else:
                    logger.info('Event "{}" is not allowed to be passed to backend "{}"'.format(event['name'], name))

            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    'Unable to send event "{}" to backend "{}"'.format(event['name'], name)
                )

    def should_event_pass(self, event, backend_name):
        """
        Return if the event is allowed to be passed to backend.

        Arguments:
            event (dict) :          event dictionary
            backend_name (str):     name of the backend against which the event is being tested

        Returns:
            bool

        Raises:
            KeyError
        """
        filter_settings = getattr(settings, ASYNC_ROUTING_FILTERS_SETTINGS_NAME, {})[backend_name]
        filter_config = FilterConfig(**filter_settings)

        self._validate_filter_type(filter_config)
        compiled_expressions = self._compile_regular_expressions(filter_config.regular_expressions)

        is_a_match = self._event_matches_filter(event['name'], compiled_expressions)

        if (
            (is_a_match and filter_config.type == ALLOWLIST) or
            (not is_a_match and filter_config.type == BLOCKLIST)
        ):
            return True
        return False

    def _validate_filter_type(self, filter_config):
        """
        Validate that the filter type is either `allowlist` or `blocklist`

        Arguments:
            namedtuple<FilterConfig>

        Raises:
            ImproperlyConfigured
        """
        if filter_config.type not in (ALLOWLIST, BLOCKLIST):
            logger.error(
                'Unsupported filter type {} is set. Allowed types are only {} and {}.'.format(
                    filter_config.type,
                    ALLOWLIST,
                    BLOCKLIST
                ))
            raise ImproperlyConfigured('Invalid filter type is configured')

    def _compile_regular_expressions(self, expressions_list):
        """
        Compile and validate every reg ex in the list and return a tuple containing
        lists of compiled and invalid expressions.

        Arguments:
            expressions_list (list) :   list of regular expression strings

        Returns:
            tuple(list<compiled re>, list<str>)
        """
        invalid_regex_expressions = []
        compiled_regex_expressions = []
        for exp in expressions_list:
            try:
                compiled = re.compile(exp)
                compiled_regex_expressions.append(compiled)
            except re.error:
                invalid_regex_expressions.append(exp)

        if invalid_regex_expressions:
            logger.error('The following invalid regular expressions are configured'
                         'for setting "ASYNC_ROUTING_BACKENDS_FILTERS": {}'.format(invalid_regex_expressions))
            raise ImproperlyConfigured('Invalid Regular Expressions are configured.')

        return compiled_regex_expressions

    def _event_matches_filter(self, event_name, expressions):
        """
        Determine if event name matches any of the regular expressions.

        Arguments:
            event_name (str):   name of the event
            expressions (list): list of compiled regular expressions

        Returns:
            bool
        """
        for expression in expressions:
            if expression.match(event_name):
                return True
        return False
