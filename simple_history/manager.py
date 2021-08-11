from django.db import connection, models
from django.db.models import OuterRef, QuerySet, Subquery
from django.utils import timezone

from simple_history.utils import get_change_reason_from_object


class HistoricalQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(HistoricalQuerySet, self).__init__(*args, **kwargs)
        self._as_instances = False
        self._orig_type = type(self.model().instance)
        self._pk_attr = self._orig_type._meta.pk.name

    def as_instances(self):
        """
        Return a queryset that generates instances instead of historical records.
        Queries against the resulting queryset will translate `pk` into the
        primary key field of the original type.

        Returns a queryset.
        """
        if not self._as_instances:
            result = self.exclude(history_type="-").order_by(self._pk_attr)
            result._as_instances = True
        else:
            result = self._clone()
        return result

    def as_of(self, date):
        """
        Obtain a point-in-time snapshot of the historical data in a queryset
        friendly way.  This is a method on a queryset so it can be chained
        with other filters to yield a complex point-in-time query.

        Returns a queryset.

        For additional history on this topic, see:
          - https://github.com/jazzband/django-simple-history/pull/229
          - https://github.com/jazzband/django-simple-history/issues/354
          - https://github.com/jazzband/django-simple-history/issues/397
        """
        queryset = self.filter(history_date__lte=date)
        # If using MySQL, need to get a list of IDs in memory and then use them for the
        # second query.
        # Does mean two loops through the DB to get the full set, but still a speed
        # improvement.
        backend = connection.vendor
        if backend == "mysql":
            history_ids = {}
            for item in queryset.order_by("-history_date", "-pk"):
                if getattr(item, self._pk_attr) not in history_ids:
                    history_ids[getattr(item, self._pk_attr)] = item.pk
            latest_historics = queryset.filter(history_id__in=history_ids.values())
        elif backend == "postgresql":
            latest_pk_attr_historic_ids = (
                queryset.order_by(self._pk_attr, "-history_date", "-pk")
                .distinct(self._pk_attr)
                .values_list("pk", flat=True)
            )
            latest_historics = queryset.filter(
                history_id__in=latest_pk_attr_historic_ids
            )
        else:
            latest_pk_attr_historic_ids = (
                queryset.filter(**{self._pk_attr: OuterRef(self._pk_attr)})
                .order_by("-history_date", "-pk")
                .values("pk")[:1]
            )
            latest_historics = queryset.filter(
                history_id__in=Subquery(latest_pk_attr_historic_ids)
            )
        return latest_historics

    def filter(self, *args, **kwargs):
        # if a `pk` filter arrives and the queryset is returning instances
        # then the caller actually wants to filter based on the original
        # type's primary key, and not the history_id (historical record's
        # primary key); this happens frequently with DRF
        if self._as_instances and "pk" in kwargs:
            kwargs[self._pk_attr] = kwargs.pop("pk")
        return super().filter(*args, **kwargs)

    def _clone(self):
        c = super()._clone()
        c._as_instances = getattr(self, "_as_instances")
        c._orig_type = getattr(self, "_orig_type")
        c._pk_attr = getattr(self, "_pk_attr")
        return c

    def _fetch_all(self):
        super()._fetch_all()
        self._instanceize()

    def _instanceize(self):
        """Convert the result cache to instances if it has not already been done."""
        if (
            self._result_cache
            and self._as_instances
            and not isinstance(self._result_cache[0], self._orig_type)
        ):
            self._result_cache = [item.instance for item in self._result_cache]


class HistoryDescriptor:
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        if instance is None:
            return HistoryManager.from_queryset(HistoricalQuerySet)(self.model)
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

        Additional filter arguments can be passed in.

        Returns an instance, or an iterable of the instances, of the
        original model with all the attributes set according to what
        was present on the object on the date provided.
        """
        if not self.instance:
            return self.get_queryset().as_of(date).as_instances()

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
