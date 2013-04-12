#!/usr/bin/env python
import sys
from os.path import abspath, dirname

from django.conf import settings


sys.path.insert(0, abspath(dirname(__file__)))


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'simple_history',
            'simple_history.tests'
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
