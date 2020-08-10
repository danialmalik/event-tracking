"""A Django settings file for testing"""

from __future__ import absolute_import

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

SITE_ID = 1

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
)

INSTALLED_APPS = [
    'eventtracking.django'
]

EVENT_TRACKING_ENABLED = True

ASYNC_ROUTING_BACKENDS = {
    'mock': {
        'ENGINE': 'mock.MagicMock'
    },
}

ASYNC_ROUTING_FILTERS = {
    'mock': {
        'type': '',
        'regular_expressions': []
    }
}

SECRET_KEY = "test_key"
