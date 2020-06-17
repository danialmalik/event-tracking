"""
Filter configured through admin panel. Filters out the events that
do not need to be routed
"""


class RoutingFilter:
    def __init__(self, **kwargs):
        pass

    def __call__(self, event, **kwargs):
        return event
