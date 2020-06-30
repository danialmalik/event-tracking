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
        from eventtracking.django.models import RegExFilter

        def _should_event_pass(event_name, regex_filter):
            match_found = False
            for expression in regex_filter.compiled_expressions:
                if re.match(expression, event_name):
                    match_found = True
                    logger.info('Event %s matches the regular expression %s with filter type '
                                'set to %s', event_name, expression, regex_filter.filter_type)
                    break

            if (
                (match_found and regex_filter.filter_type == RegExFilter.BLACKLIST)
                or
                (not match_found and regex_filter.filter_type == RegExFilter.WHITELIST)
            ):
                return False
            return True

        try:
            regex_filter = RegExFilter.objects.all()[0]
        except IndexError:
            logger.warning('Regular Expression Filter does not have any configurations. '
                           'Cannot filter events.')
            return event

        event_name = event.get('event_type')

        if not _should_event_pass(event_name, regex_filter):
            logger.info('Event %s is not allowed to be further processed.', event_name)
            raise EventEmissionExit
        else:
            import pdb; pdb.set_trace()
            logger.info('Event %s is allowed to be further processed.', event_name)
            return event
