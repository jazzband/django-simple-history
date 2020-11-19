#!/usr/bin/env python
import logging
import sys
from argparse import ArgumentParser
from os.path import abspath, dirname, join
from shutil import rmtree

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

sys.path.insert(0, abspath(dirname(__file__)))

media_root = join(abspath(dirname(__file__)), "test_files")
rmtree(media_root, ignore_errors=True)

installed_apps = [
    "simple_history.tests",
    "simple_history.tests.custom_user",
    "simple_history.tests.external",
    "simple_history.registry_tests.migration_test_app",
    "simple_history",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.messages",
]


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


DATABASE_NAME_TO_BACKEND = {
    "sqlite3": "django.db.backends.sqlite3",
    "postgres": "django.db.backends.postgresql",
}


DEFAULT_SETTINGS = dict(
    SECRET_KEY="not a secret",
    ALLOWED_HOSTS=["localhost"],
    AUTH_USER_MODEL="custom_user.CustomUser",
    ROOT_URLCONF="simple_history.tests.urls",
    MEDIA_ROOT=media_root,
    STATIC_URL="/static/",
    INSTALLED_APPS=installed_apps,
    LOGGING={
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
    MIGRATION_MODULES=DisableMigrations(),
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ],
)
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

DEFAULT_SETTINGS["MIDDLEWARE"] = MIDDLEWARE


def main():
    parser = ArgumentParser(description="Run package tests.")
    parser.add_argument("--tag", action="append", nargs="?")
    parser.add_argument("--database", action="store", nargs="?", default="sqlite3")
    namespace = parser.parse_args()
    db_engine = DATABASE_NAME_TO_BACKEND[namespace.database]
    if not settings.configured:
        settings.configure(
            **DEFAULT_SETTINGS,
            DATABASES={
                "default": {
                    "ENGINE": db_engine,
                    "NAME": "test",
                },
                "other": {
                    "ENGINE": db_engine,
                    "NAME": "test",
                },
            },
        )

    django.setup()

    tags = namespace.tag
    failures = DiscoverRunner(failfast=False, tags=tags).run_tests(
        ["simple_history.tests"]
    )
    failures |= DiscoverRunner(failfast=False, tags=tags).run_tests(
        ["simple_history.registry_tests"]
    )
    sys.exit(failures)


if __name__ == "__main__":
    main()
