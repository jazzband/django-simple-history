from django.db import connection, models
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from simple_history.utils import get_change_reason_from_object


class HistoryDescriptor:
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        if instance is None:
            return HistoryManager(self.model)
        return HistoryManager(self.model, instance)


class HistoryManager(models.Manager):
    def __init__(self, model, instance=None):
        super(HistoryManager, self).__init__()
        self.model = model
        self.instance = instance

    def get_super_queryset(self):
        return super(HistoryManager, self).get_queryset()

    def get_queryset(self):
        qs = self.get_super_queryset()
        if self.instance is None:
            return qs

        if isinstance(self.instance._meta.pk, models.ForeignKey):
            key_name = self.instance._meta.pk.name + "_id"
        else:
            key_name = self.instance._meta.pk.name
        return self.get_super_queryset().filter(**{key_name: self.instance.pk})

    def most_recent(self):
        """
        Returns the most recent copy of the instance available in the history.
        """
        if not self.instance:
            raise TypeError(
                "Can't use most_recent() without a {} instance.".format(
                    self.model._meta.object_name
                )
            )
        tmp = []
        excluded_fields = getattr(self.model, "_history_excluded_fields", [])

        for field in self.instance._meta.fields:
            if field.name in excluded_fields:
                continue
            if isinstance(field, models.ForeignKey):
                tmp.append(field.name + "_id")
            else:
                tmp.append(field.name)
        fields = tuple(tmp)
        try:
            values = self.get_queryset().values(*fields)[0]
        except IndexError:
            raise self.instance.DoesNotExist(
                "%s has no historical record." % self.instance._meta.object_name
            )
        return self.instance.__class__(**values)

    def as_of(self, date):
        """Get a snapshot as of a specific date.

        Returns an instance, or an iterable of the instances, of the
        original model with all the attributes set according to what
        was present on the object on the date provided.
        """
        if not self.instance:
            return self._as_of_set(date)
        queryset = self.get_queryset().filter(history_date__lte=date)
        try:
            history_obj = queryset[0]
        except IndexError:
            raise self.instance.DoesNotExist(
                "%s had not yet been created." % self.instance._meta.object_name
            )
        if history_obj.history_type == "-":
            raise self.instance.DoesNotExist(
                "%s had already been deleted." % self.instance._meta.object_name
            )
        return history_obj.instance

    def _as_of_set(self, date):
        model = type(self.model().instance)  # a bit of a hack to get the model
        pk_attr = model._meta.pk.name
        queryset = self.get_queryset().filter(history_date__lte=date)
        # If using MySQL, need to get a list of IDs in memory and then use them for the
        # second query.
        # Does mean two loops through the DB to get the full set, but still a speed
        # improvement.
        backend = connection.vendor
        if backend == "mysql":
            history_ids = {}
            for item in queryset.order_by("-history_date", "-pk"):
                if getattr(item, pk_attr) not in history_ids:
                    history_ids[getattr(item, pk_attr)] = item.pk
            latest_historics = queryset.filter(history_id__in=history_ids.values())
        elif backend == "postgresql":
            latest_pk_attr_historic_ids = (
                queryset.order_by(pk_attr, "-history_date", "-pk")
                .distinct(pk_attr)
                .values_list("pk", flat=True)
            )
            latest_historics = queryset.filter(
                history_id__in=latest_pk_attr_historic_ids
            )
        else:
            latest_pk_attr_historic_ids = (
                queryset.filter(**{pk_attr: OuterRef(pk_attr)})
                .order_by("-history_date", "-pk")
                .values("pk")[:1]
            )
            latest_historics = queryset.filter(
                history_id__in=Subquery(latest_pk_attr_historic_ids)
            )
        adjusted = latest_historics.exclude(history_type="-").order_by(pk_attr)
        for historic_item in adjusted:
            yield historic_item.instance

    def bulk_history_create(
        self,
        objs,
        batch_size=None,
        update=False,
        default_user=None,
        default_change_reason="",
        default_date=None,
    ):
        """
        Bulk create the history for the objects specified by objs.
        If called by bulk_update_with_history, use the update boolean and
        save the history_type accordingly.
        """

        history_type = "+"
        if update:
            history_type = "~"

        historical_instances = []
        for instance in objs:
            history_user = getattr(
                instance,
                "_history_user",
                default_user or self.model.get_default_history_user(instance),
            )
            row = self.model(
                history_date=getattr(
                    instance, "_history_date", default_date or timezone.now()
                ),
                history_user=history_user,
                history_change_reason=get_change_reason_from_object(instance)
                or default_change_reason,
                history_type=history_type,
                **{
                    field.attname: getattr(instance, field.attname)
                    for field in instance._meta.fields
                    if field.name not in self.model._history_excluded_fields
                },
            )
            if hasattr(self.model, "history_relation"):
                row.history_relation_id = instance.pk
            historical_instances.append(row)

        return self.model.objects.bulk_create(
            historical_instances, batch_size=batch_size
        )
