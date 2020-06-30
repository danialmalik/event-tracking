"""
Models for filtering of events
"""
import logging
import re

from django.core.exceptions import ValidationError
from django.db import models

LOGGER = logging.getLogger(__name__)


class RegExFilter(models.Model):
    BLACKLIST = 'blacklist'
    WHITELIST = 'whitelist'
    FILTER_TYPES = (
        (BLACKLIST, 'Blacklist'),
        (WHITELIST, 'Whitelist'),
    )

    is_enabled = models.BooleanField(
        default=True,
        verbose_name='Is Enabled'
    )

    filter_type = models.CharField(
        max_length=9,
        choices=FILTER_TYPES,
        verbose_name='Filter type',
        help_text=(
            'Whitelist: Only events matching the regular expressions in the list '
            'will be allowed to passed through.'
            '<br/>'
            'Blacklist: Events matching any regular expression in the list will be '
            'blocked.')
    )

    regular_expressions = models.TextField(
        max_length=500,
        verbose_name='List of regular expressions',
        help_text=('This should be a comma-seperated list of regular'
                   ' expressions for the events to be filtered.')
    )

    def save(self, *args, **kwargs):
        if not self.pk and RegExFilter.objects.exists():
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There can be only one RegExFilter instance')
        return super(RegExFilter, self).save(*args, **kwargs)

    @property
    def compiled_expressions(self):
        raw_expressions = self.regular_expressions.split(',')
        raw_expressions = [expression.strip() for expression in raw_expressions]
        compiled = []
        for expression in raw_expressions:
            try:
                compiled.append(re.compile(expression))
            except re.error:
                LOGGER.error('Invalid expression passed in expressions list: %s', expression)

        return compiled
