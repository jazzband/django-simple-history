from django.db import transaction

from simple_history.exceptions import NotHistoricalModelError


def update_change_reason(instance, reason):
    attrs = {}
    model = type(instance)
    manager = instance if instance.id is not None else model
    for field in instance._meta.fields:
        value = getattr(instance, field.attname)
        if field.primary_key is True:
            if value is not None:
                attrs[field.attname] = value
        else:
            attrs[field.attname] = value
    record = manager.history.filter(**attrs).order_by('-history_date').first()
    record.history_change_reason = reason
    record.save()


def get_history_manager_for_model(model):
    """Return the history manager for a given app model."""
    try:
        manager_name = model._meta.simple_history_manager_attribute
    except AttributeError:
        raise NotHistoricalModelError(
            "Cannot find a historical model for {model}.".format(model=model)
        )
    return getattr(model, manager_name)


def get_history_model_for_model(model):
    """Return the history model for a given app model."""
    return get_history_manager_for_model(model).model


def bulk_create_with_history(objs, model, batch_size=None):
    """
    Bulk create the objects specified by objs while also bulk creating
    their history (all in one transaction).
    :param objs: List of objs (not yet saved to the db) of type model
    :param model: Model class that should be created
    :param batch_size: Number of objects that should be created in each batch
    :return: List of objs with IDs
    """

    history_manager = get_history_manager_for_model(model)

    with transaction.atomic(savepoint=False):
        objs_with_id = model.objects.bulk_create(objs, batch_size=batch_size)
        history_manager.bulk_history_create(objs_with_id,
                                            batch_size=batch_size)

    return objs_with_id
