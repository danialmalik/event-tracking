"""Filter out events whose names aren't on a pre-configured whitelist"""

from __future__ import absolute_import

import six

from eventtracking.processors.exceptions import EventEmissionExit


class NameWhitelistProcessor:
    """

    Filter out events whose names aren't on a pre-configured whitelist.

    `whitelist` is an iterable collection containing event names that should be allowed to pass.
    """

    def __init__(self, whitelist=None, **_kwargs):
        try:
            if isinstance(whitelist, six.string_types):
                raise TypeError

            self.whitelist = frozenset(whitelist)
        except TypeError:
            raise TypeError(
                'The NameWhitelistProcessor must be passed a collection of allowed names '
                'using the "whitelist" parameter'
            )

    def __call__(self, event):
        if event['name'] not in self.whitelist:
            raise EventEmissionExit()

        return event
