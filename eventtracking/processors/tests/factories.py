"""Factories needed for unit tests in the app"""

import factory
from django.apps import apps


class RegExFilterFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('django', 'RegExFilter')
