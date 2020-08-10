"""
Tests for celery tasks
"""
import json

from django.test import TestCase

from mock import MagicMock, patch, sentinel

from eventtracking.tasks import async_send


class TestAsyncSend(TestCase):
    """Test async_send task"""

    def setUp(self):
        super(TestAsyncSend, self).setUp()

        self.event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'event': {
                'key': 'value'
            },
            'session': '0000'
        }

        self.backend_name = 'test'
        self.mocked_backend = MagicMock()

    @patch('eventtracking.tasks.AsyncTracker')
    def test_event_is_passed_to_async_tracker(self, mocked_async_tracker_cls):
        mocked_tracker = MagicMock()
        mocked_async_tracker_cls.return_value = mocked_tracker

        async_send('test_settings_name', json.dumps(self.event))
        mocked_tracker.send_to_backends.assert_called_once_with(self.event)
