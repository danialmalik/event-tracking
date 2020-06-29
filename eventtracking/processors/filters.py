"""
Filter configured through admin panel. Filters out the events that
do not need to be routed
"""
import re
import logging

from eventtracking.processors.exceptions import EventEmissionExit

logger = logging.getLogger(__name__)


class RegExFilterProcessor:
    """
    Filter the events using regex. The regex list Can be configured
    through the Admin panel.
    """

    def __call__(self, event, **kwargs):
        from eventtracking.django.models import RegExpFilter

        try:
            regex_filter = RegExpFilter.objects.all()[0]
        except IndexError:
            logger.warning('Regular Expression Filter does not have any configurations. \
                            Cannot filter events.')
            return event

        regular_expressions = regex_filter.regular_expressions
        if regular_expressions:
            regular_expressions = regular_expressions.split(',')
            regular_expressions = [expression.strip() for expression in regular_expressions]

        event_name = event.get('event_type')
        match_found = False

        for expression in regular_expressions:
            try:
                expression = re.compile(expression)
            except re.error:
                logger.error('Invalid regular expression passed: %s.\
                               Cannot process using this expression.', expression)
                continue

            if re.match(expression, event_name):
                match_found = True
                logger.info('Event %s matches the regular expression %s with filter type \
                            set to %s', event_name, expression, regex_filter.filter_type)
                break

        if (
            (match_found and regex_filter.filter_type == RegExpFilter.BLACKLIST)
            or
            (not match_found and regex_filter.filter_type == RegExpFilter.WHITELIST)
        ):
            logger.info('Event %s is not allowed to be further processed.', event_name)
            raise EventEmissionExit

        elif (
            (match_found and regex_filter.filter_type == RegExpFilter.WHITELIST)
            or
            (not match_found and regex_filter.filter_type == RegExpFilter.BLACKLIST)
        ):
            logger.info('Event %s is allowed to be further processed.')
            return event
