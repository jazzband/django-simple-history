from __future__ import unicode_literals

from . import models


registered_models = models.registered_models


def register(model, app=None, manager_name='history'):
    """
    Create historical model for `model` and attach history manager to `model`.

    Keyword arguments:
    app -- App to install historical model into (defaults to model.__module__)
    manager_name -- class attribute name to use for historical manager

    This method should be used as an alternative to attaching an
    `HistoricalManager` instance directly to `model`.
    """
    if not model._meta.db_table in registered_models:
        records = models.HistoricalRecords()
        records.manager_name = manager_name
        records.module = app and ("%s.models" % app) or model.__module__
        records.finalize(model)
        registered_models[model._meta.db_table] = model
