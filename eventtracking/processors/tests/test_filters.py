
"""Test the filter processor(s)"""
import ddt
import pytest
from mock import patch
from mock import sentinel
from unittest import TestCase

from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.processors.filters import RegExFilterProcessor
from eventtracking.processors.tests.factories import RegExFilterFactory

# Let pytest know that DB is accessible for user.
pytestmark = pytest.mark.django_db

@ddt.ddt
@patch('eventtracking.processors.filters.logger')
class RegExFilterProcessorTests(TestCase):
    """
    Tests RegExFilterProcessor with different possible scenarios.
    """
    @classmethod
    def setUpClass(cls):
        super(RegExFilterProcessorTests, cls).setUpClass()
        cls.filter = RegExFilterProcessor()

    def test_with_no_filter_setup(self, mocked_logger):
        """
        Tests the processor when there is no filter processor setup.
        """
        event = {
            'name': sentinel.name,
            'context': {
                'user_id': sentinel.user_id
            },
            'data': {
                'foo': sentinel.bar
            }
        }
        result = self.filter(event)
        self.assertDictEqual(event, result)
        mocked_logger.warning.assert_called_once_with(
            'Regular Expression Filter does not have any configurations. '
            'Cannot filter events.'
        )

    @ddt.data(
        ('whitelist', 'sentinel.*', sentinel.name, True),
        ('whitelist', 'NOT_MATCHING', sentinel.name, False),
        ('blacklist', 'sentinel.*', sentinel.name, False),
        ('blacklist', 'NOT_MATCHING', sentinel.name, True),
    )
    @ddt.unpack
    def test_event_passing_multiple_scenarios(self, filter_type, filter_regex, event_name, should_pass, mocked_logger):
        RegExFilterFactory.create(is_enabled=True, filter_type=filter_type, regular_expressions=filter_regex)
        event = {
            'name': str(event_name),
            'context': {
                'user_id': sentinel.user_id
            },
            'data': {
                'foo': sentinel.bar
            }
        }
        if not should_pass:
            with self.assertRaises(EventEmissionExit):
                self.filter(event)
        else:
            result = self.filter(event)
            self.assertEqual(event, result)
