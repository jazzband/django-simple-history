#!/usr/bin/env python
import sys
from shutil import rmtree
from os.path import abspath, dirname, join

import django
from django.conf import settings


sys.path.insert(0, abspath(dirname(__file__)))


media_root = join(abspath(dirname(__file__)), 'test_files')
rmtree(media_root, ignore_errors=True)

installed_apps = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'simple_history',
    'simple_history.tests',
    'simple_history.tests.external',
    'simple_history.tests.migration_test_app',
]

DEFAULT_SETTINGS = dict(
    ROOT_URLCONF='simple_history.tests.urls',
    MEDIA_ROOT=media_root,
    STATIC_URL='/static/',
    INSTALLED_APPS=installed_apps,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
)

if django.VERSION >= (1, 5):
    installed_apps.append('simple_history.tests.custom_user')
    DEFAULT_SETTINGS['AUTH_USER_MODEL'] = 'custom_user.CustomUser'

def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    if hasattr(django, 'setup'):
        django.setup()
    try:
        from django.test.runner import DiscoverRunner
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner
        failures = DjangoTestSuiteRunner(failfast=False).run_tests(['tests'])
    else:
        failures = DiscoverRunner(failfast=False).run_tests(
            ['simple_history.tests'])
    sys.exit(failures)


if __name__ == "__main__":
    main()
