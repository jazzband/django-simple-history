import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, ClassVar, Iterator, Optional, Type, Union

from asgiref.local import Local
from django.conf import settings
from django.db import transaction
from django.db.models import Case, ForeignKey, ManyToManyField, Model, Q, When
from django.forms.models import model_to_dict

from .exceptions import AlternativeManagerError, NotHistoricalModelError

if TYPE_CHECKING:
    from .manager import HistoricalQuerySet, HistoryManager
    from .models import HistoricalChanges


@contextmanager
def disable_history(
    *,
    only_for_model: Type[Model] = None,
    instance_predicate: Callable[[Model], bool] = None,
) -> Iterator[None]:
    """
    Disable creating historical records while this context manager is active.

    Note: ``only_for_model`` and ``instance_predicate`` cannot both be provided.

    :param only_for_model: Only disable history creation for this model type.
    :param instance_predicate: Only disable history creation for model instances passing
        this predicate.
    """
    assert (  # nosec
        _StoredDisableHistoryInfo.get() is None
    ), "Nesting 'disable_history()' contexts is undefined behavior"

    if only_for_model:
        # Raise an error if it's not a history-tracked model
        get_history_manager_for_model(only_for_model)
        if instance_predicate:
            raise ValueError(
                "'only_for_model' and 'instance_predicate' cannot both be provided"
            )
        else:

            def instance_predicate(instance: Model):
                return isinstance(instance, only_for_model)

    info = _StoredDisableHistoryInfo(instance_predicate)
    info.set()
    try:
        yield
    finally:
        info.delete()


@dataclass(frozen=True)
class _StoredDisableHistoryInfo:
    """
    Data related to how historical record creation is disabled, stored in
    ``HistoricalRecords.context`` through the ``disable_history()`` context manager.
    """

    LOCAL_STORAGE_ATTR_NAME: ClassVar = "disable_history_info"

    instance_predicate: Callable[[Model], bool] = None

    def set(self) -> None:
        setattr(self._get_storage(), self.LOCAL_STORAGE_ATTR_NAME, self)

    @classmethod
    def get(cls) -> Optional["_StoredDisableHistoryInfo"]:
        """
        A return value of ``None`` means that the ``disable_history()`` context manager
        is not active.
        """
        return getattr(cls._get_storage(), cls.LOCAL_STORAGE_ATTR_NAME, None)

    @classmethod
    def delete(cls) -> None:
        delattr(cls._get_storage(), cls.LOCAL_STORAGE_ATTR_NAME)

    @staticmethod
    def _get_storage() -> Local:
        from .models import HistoricalRecords  # Avoids circular importing

        return HistoricalRecords.context


@dataclass(
    frozen=True,
    # DEV: Replace this with just `kw_only=True` when the minimum required
    #      Python version is 3.10
    **({"kw_only": True} if sys.version_info >= (3, 10) else {}),
)
class DisableHistoryInfo:
    """
    Provides info on *how* historical record creation is disabled.

    Create a new instance through ``get()`` for updated info.
    (The ``__init__()`` method is intended for internal use.)
    """

    _disabled_globally: bool
    _instance_predicate: Optional[Callable[[Model], bool]]

    @property
    def not_disabled(self) -> bool:
        """
        A value of ``True`` means that historical record creation is not disabled
        in any way.
        If ``False``, check ``disabled_globally`` and ``disabled_for()``.
        """
        return not self._disabled_globally and not self._instance_predicate

    @property
    def disabled_globally(self) -> bool:
        """
        Whether historical record creation is disabled due to
        the ``SIMPLE_HISTORY_ENABLED`` setting or the ``disable_history()`` context
        manager being active.
        """
        return self._disabled_globally

    def disabled_for(self, instance: Model) -> bool:
        """
        Returns whether history record creation is disabled for the provided instance
        specifically.
        Remember to also check ``disabled_globally``!
        """
        return bool(self._instance_predicate) and self._instance_predicate(instance)

    @classmethod
    def get(cls) -> "DisableHistoryInfo":
        """
        Returns an instance of this class.

        Note that this method must be called again every time you want updated info.
        """
        stored_info = _StoredDisableHistoryInfo.get()
        context_manager_active = bool(stored_info)
        instance_predicate = (
            stored_info.instance_predicate if context_manager_active else None
        )

        disabled_globally = not getattr(settings, "SIMPLE_HISTORY_ENABLED", True) or (
            context_manager_active and not instance_predicate
        )
        return cls(
            _disabled_globally=disabled_globally,
            _instance_predicate=instance_predicate,
        )


def is_history_disabled(instance: Model = None) -> bool:
    """
    Returns whether creating historical records is disabled.

    :param instance: If *not* provided, will return whether history is disabled
        globally. Otherwise, will return whether history is disabled for the provided
        instance (either globally or due to the arguments passed to
        the ``disable_history()`` context manager).
    """
    if instance:
        # Raise an error if it's not a history-tracked model instance
        get_history_manager_for_model(instance)

    info = DisableHistoryInfo.get()
    if info.disabled_globally:
        return True
    if instance and info.disabled_for(instance):
        return True
    return False


def get_change_reason_from_object(obj: Model) -> Optional[str]:
    return getattr(obj, "_change_reason", None)


def update_change_reason(instance: Model, reason: Optional[str]) -> None:
    attrs = {}
    model = type(instance)
    manager = instance if instance.pk is not None else model
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


def get_history_manager_for_model(
    model_or_instance: Union[Type[Model], Model]
) -> "HistoryManager":
    """Return the history manager for ``model_or_instance``.

    :raise NotHistoricalModelError: If the model has not been registered to track
        history.
    """
    try:
        manager_name = model_or_instance._meta.simple_history_manager_attribute
    except AttributeError:
        raise NotHistoricalModelError(
            f"Cannot find a historical model for {model_or_instance}."
        )
    return getattr(model_or_instance, manager_name)


def get_history_model_for_model(
    model_or_instance: Union[Type[Model], Model]
) -> Type["HistoricalChanges"]:
    """Return the history model for ``model_or_instance``.

    :raise NotHistoricalModelError: If the model has not been registered to track
        history.
    """
    return get_history_manager_for_model(model_or_instance).model


def get_historical_records_of_instance(
    historical_record: "HistoricalChanges",
) -> "HistoricalQuerySet":
    """
    Return a queryset with all the historical records of the same instance as
    ``historical_record`` is for.
    """
    pk_name = get_pk_name(historical_record.instance_type)
    manager = get_history_manager_for_model(historical_record.instance_type)
    return manager.filter(**{pk_name: getattr(historical_record, pk_name)})


def get_pk_name(model: Type[Model]) -> str:
    """Return the primary key name for ``model``."""
    if isinstance(model._meta.pk, ForeignKey):
        return f"{model._meta.pk.name}_id"
    return model._meta.pk.name


def get_m2m_field_name(m2m_field: ManyToManyField) -> str:
    """
    Returns the field name of an M2M field's through model that corresponds to the model
    the M2M field is defined on.

    E.g. for a ``votes`` M2M field on a ``Poll`` model that references a ``Vote`` model
    (and with a default-generated through model), this function would return ``"poll"``.
    """
    # This method is part of Django's internal API
    return m2m_field.m2m_field_name()


def get_m2m_reverse_field_name(m2m_field: ManyToManyField) -> str:
    """
    Returns the field name of an M2M field's through model that corresponds to the model
    the M2M field references.

    E.g. for a ``votes`` M2M field on a ``Poll`` model that references a ``Vote`` model
    (and with a default-generated through model), this function would return ``"vote"``.
    """
    # This method is part of Django's internal API
    return m2m_field.m2m_reverse_field_name()


def bulk_create_with_history(
    objs,
    model,
    batch_size=None,
    ignore_conflicts=False,
    default_user=None,
    default_change_reason=None,
    default_date=None,
    custom_historical_attrs=None,
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
    :param default_date: Optional date to specify as the history_date in each historical
        record
    :param custom_historical_attrs: Optional dict of field `name`:`value` to specify
        values for custom fields
    :return: List of objs with IDs
    """
    # Exclude ManyToManyFields because they end up as invalid kwargs to
    # model.objects.filter(...) below.
    exclude_fields = [
        field.name
        for field in model._meta.get_fields()
        if isinstance(field, ManyToManyField)
    ]
    history_manager = get_history_manager_for_model(model)
    model_manager = model._default_manager

    second_transaction_required = True
    with transaction.atomic(savepoint=False):
        objs_with_id = model_manager.bulk_create(
            objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts
        )
        if objs_with_id and objs_with_id[0].pk and not ignore_conflicts:
            second_transaction_required = False
            history_manager.bulk_history_create(
                objs_with_id,
                batch_size=batch_size,
                default_user=default_user,
                default_change_reason=default_change_reason,
                default_date=default_date,
                custom_historical_attrs=custom_historical_attrs,
            )
    if second_transaction_required:
        with transaction.atomic(savepoint=False):
            # Generate a common query to avoid n+1 selections
            #   https://github.com/jazzband/django-simple-history/issues/974
            cumulative_filter = None
            obj_when_list = []
            for i, obj in enumerate(objs_with_id):
                attributes = dict(
                    filter(
                        lambda x: x[1] is not None,
                        model_to_dict(obj, exclude=exclude_fields).items(),
                    )
                )
                q = Q(**attributes)
                cumulative_filter = (cumulative_filter | q) if cumulative_filter else q
                # https://stackoverflow.com/a/49625179/1960509
                # DEV: If an attribute has `then` as a key
                #   then they'll also run into issues with `bulk_update`
                #   due to shared implementation
                #   https://github.com/django/django/blob/4.0.4/django/db/models/query.py#L624-L638
                obj_when_list.append(When(**attributes, then=i))
            obj_list = (
                list(
                    model_manager.filter(cumulative_filter).order_by(
                        Case(*obj_when_list)
                    )
                )
                if objs_with_id
                else []
            )
            history_manager.bulk_history_create(
                obj_list,
                batch_size=batch_size,
                default_user=default_user,
                default_change_reason=default_change_reason,
                default_date=default_date,
                custom_historical_attrs=custom_historical_attrs,
            )
        objs_with_id = obj_list
    return objs_with_id


def bulk_update_with_history(
    objs,
    model,
    fields,
    batch_size=None,
    default_user=None,
    default_change_reason=None,
    default_date=None,
    manager=None,
    custom_historical_attrs=None,
):
    """
    Bulk update the objects specified by objs while also bulk creating
    their history (all in one transaction).
    :param objs: List of objs of type model to be updated
    :param model: Model class that should be updated
    :param fields: The fields that are updated. If empty, no model objects will be
        changed, but history records will still be created.
    :param batch_size: Number of objects that should be updated in each batch
    :param default_user: Optional user to specify as the history_user in each historical
        record
    :param default_change_reason: Optional change reason to specify as the change_reason
        in each historical record
    :param default_date: Optional date to specify as the history_date in each historical
        record
    :param manager: Optional model manager to use for the model instead of the default
        manager
    :param custom_historical_attrs: Optional dict of field `name`:`value` to specify
        values for custom fields
    :return: The number of model rows updated, not including any history objects
    """
    history_manager = get_history_manager_for_model(model)
    model_manager = manager or model._default_manager
    if model_manager.model is not model:
        raise AlternativeManagerError("The given manager does not belong to the model.")

    with transaction.atomic(savepoint=False):
        if not fields:
            # Allow not passing any fields if the user wants to bulk-create history
            # records - e.g. with `custom_historical_attrs` provided
            # (Calling `bulk_update()` with no fields would have raised an error)
            rows_updated = 0
        else:
            rows_updated = model_manager.bulk_update(
                objs, fields, batch_size=batch_size
            )
        history_manager.bulk_history_create(
            objs,
            batch_size=batch_size,
            update=True,
            default_user=default_user,
            default_change_reason=default_change_reason,
            default_date=default_date,
            custom_historical_attrs=custom_historical_attrs,
        )
    return rows_updated
