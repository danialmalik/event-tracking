"""
Test the AsyncTracker.
"""
import ddt
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from mock import sentinel

from eventtracking.async_tracker import (
    AsyncTracker,
    ALLOWLIST,
    BLOCKLIST,
    ASYNC_ROUTING_BACKENDS_SETTINGS_NAME
)


@ ddt.ddt
class TestAsyncTracker(TestCase):
    """
    Test the AsyncTracker.
    """

    def setUp(self):
        super(TestAsyncTracker, self).setUp()
        self.event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'event': {
                'key': 'value'
            },
            'session': '0000'
        }
        self.tracker = AsyncTracker(backends_settings_name=ASYNC_ROUTING_BACKENDS_SETTINGS_NAME)

    @ ddt.data(
        (ALLOWLIST, ['sentinel.name', 'any'], True),
        (ALLOWLIST, ['not_matching', 'NOT_MATCHING'], False),
        (ALLOWLIST, [''], True),
        (ALLOWLIST, [], False),
        (BLOCKLIST, ['sentinel.name', 'any'], False),
        (BLOCKLIST, ['not_matching', 'NOT_MATCHING'], True),
        (BLOCKLIST, [''], False),
        (BLOCKLIST, [], True),
    )
    @ ddt.unpack
    def test_with_multiple_regex(self, filter_type, expressions, should_pass):
        async_routing_filter_settings = settings.ASYNC_ROUTING_FILTERS
        async_routing_filter_settings['mock']['type'] = filter_type
        async_routing_filter_settings['mock']['regular_expressions'] = expressions

        with override_settings(ASYNC_ROUTING_FILTERS=async_routing_filter_settings):
            self.tracker.send_to_backends(self.event)
            if should_pass:
                self.tracker.backends['mock'].send.assert_called_once_with(self.event)
            else:
                self.tracker.backends['mock'].send.assert_not_called()

    def test_exceptions_are_raised(self):
        mocked_backend = self.tracker.backends['mock']

        # test with no filters set,
        self.tracker.send_to_backends(self.event)
        mocked_backend.assert_not_called()

        # test with invalid filter type
        filter_settings = {
            'mock': {
                'type': 'INVALID_TYPE',
                'regular_expressions': []
            }
        }

        with override_settings(ASYNC_ROUTING_FILTERS=filter_settings):
            self.tracker.send_to_backends(self.event)
            mocked_backend.assert_not_called()

        # test with invalid regular expression
        filter_settings = {
            'mock': {
                'type': 'INVALID_TYPE',
                'regular_expressions': ['***']
            }
        }

        with override_settings(ASYNC_ROUTING_FILTERS=filter_settings):
            self.tracker.send_to_backends(self.event)
            mocked_backend.assert_not_called()
