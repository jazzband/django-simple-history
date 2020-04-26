import warnings

import django
from django.db import transaction
from django.forms.models import model_to_dict

from simple_history.exceptions import NotHistoricalModelError


def update_change_reason(instance, reason):
    attrs = {}
    model = type(instance)
    manager = instance if instance.id is not None else model
    history = get_history_manager_for_model(manager)
    history_fields = [field.attname for field in history.model._meta.fields]
    for field in instance._meta.fields:
        if field.attname not in history_fields:
            continue
        value = getattr(instance, field.attname)
        if field.primary_key is True:
            if value is not None:
                attrs[field.attname] = value
        else:
            attrs[field.attname] = value

    record = history.filter(**attrs).order_by("-history_date").first()
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


def bulk_create_with_history(
    objs, model, batch_size=None, default_user=None, default_change_reason=None
):
    """
    Bulk create the objects specified by objs while also bulk creating
    their history (all in one transaction).
    Because of not providing primary key attribute after bulk_create on any DB except
    Postgres (https://docs.djangoproject.com/en/2.2/ref/models/querysets/#bulk-create)
    Divide this process on two transactions for other DB's
    :param objs: List of objs (not yet saved to the db) of type model
    :param model: Model class that should be created
    :param batch_size: Number of objects that should be created in each batch
    :param default_user: Optional user to specify as the history_user in each historical
        record
    :param default_change_reason: Optional change reason to specify as the change_reason
        in each historical record
    :return: List of objs with IDs
    """

    history_manager = get_history_manager_for_model(model)
    second_transaction_required = True
    with transaction.atomic(savepoint=False):
        objs_with_id = model.objects.bulk_create(objs, batch_size=batch_size)
        if objs_with_id and objs_with_id[0].pk:
            second_transaction_required = False
            history_manager.bulk_history_create(
                objs_with_id,
                batch_size=batch_size,
                default_user=default_user,
                default_change_reason=default_change_reason,
            )
    if second_transaction_required:
        obj_list = []
        with transaction.atomic(savepoint=False):
            for obj in objs_with_id:
                attributes = dict(
                    filter(lambda x: x[1] is not None, model_to_dict(obj).items())
                )
                obj_list += model.objects.filter(**attributes)
            history_manager.bulk_history_create(
                obj_list,
                batch_size=batch_size,
                default_user=default_user,
                default_change_reason=default_change_reason,
            )
        objs_with_id = obj_list
    return objs_with_id


def bulk_update_with_history(
    objs, model, fields, batch_size=None, default_user=None, default_change_reason=None,
):
    """
    Bulk update the objects specified by objs while also bulk creating
    their history (all in one transaction).
    :param objs: List of objs of type model to be updated
    :param model: Model class that should be updated
    :param fields: The fields that are updated
    :param batch_size: Number of objects that should be updated in each batch
    :param default_user: Optional user to specify as the history_user in each historical
        record
    :param default_change_reason: Optional change reason to specify as the change_reason
        in each historical record
    """
    if django.VERSION < (2, 2,):
        raise NotImplementedError(
            "bulk_update_with_history is only available on "
            "Django versions 2.2 and later"
        )
    history_manager = get_history_manager_for_model(model)
    with transaction.atomic(savepoint=False):
        model.objects.bulk_update(
            objs, fields, batch_size=batch_size,
        )
        history_manager.bulk_history_create(
            objs,
            batch_size=batch_size,
            update=True,
            default_user=default_user,
            default_change_reason=default_change_reason,
        )


def get_change_reason_from_object(obj):
    if hasattr(obj, "_change_reason"):
        return getattr(obj, "_change_reason")

    if hasattr(obj, "changeReason"):
        warning_msg = (
            "Using the attr changeReason to populate history_change_reason is"
            " deprecated in 2.10.0 and will be removed in 3.0.0. Use "
            "_change_reason instead. "
        )
        warnings.warn(warning_msg, DeprecationWarning)
        return getattr(obj, "changeReason")

    return None
