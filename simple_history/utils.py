"""Utility functions that don't depend on the rest of the app."""


def natural_key_from_model(model):
    opts = model._meta
    try:
        return opts.app_label, opts.model_name
    except AttributeError:
        return opts.app_label, opts.module_name
