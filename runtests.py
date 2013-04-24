#!/usr/bin/env python
import sys
from shutil import rmtree
from os.path import abspath, dirname, join

from django.conf import settings


sys.path.insert(0, abspath(dirname(__file__)))


if not settings.configured:
    media_root = join(abspath(dirname(__file__)), 'test_files')
    rmtree(media_root, ignore_errors=True)
    settings.configure(
        ROOT_URLCONF='simple_history.tests.urls',
        MEDIA_ROOT=media_root,
        STATIC_URL='/static/',
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.admin',
            'simple_history',
            'simple_history.tests',
            'simple_history.tests.external'
        ),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
    )


def main():
    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner(
        verbosity=1, interactive=True, failfast=False).run_tests(['tests'])
    sys.exit(failures)


if __name__ == "__main__":
    main()
