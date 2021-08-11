from django.db import connection, models
from django.db.models import OuterRef, QuerySet, Subquery
from django.utils import timezone

from simple_history.exceptions import CannotSwitchQuerySetResultTypeError
from simple_history.utils import get_change_reason_from_object


class HistoricalQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pk_attr = type(self.model().instance)._meta.pk.name

    def as_original(self):
        """
        Tells the QuerySet you are looking for genuine records to be generated
        instead of the default behavior whichgenerates historical records.  You
        cannot switch modes after results have been fetched.
        """
        if self._result_cache:
            raise CannotSwitchQuerySetResultTypeError()

        self._as_original = True
        return self

    def _clone(self):
        c = super()._clone()
        setattr(c, "_as_original", getattr(self, "_as_original", False))
        setattr(c, "_originalized", getattr(self, "_originalized", False))
        return c

    def _fetch_all(self):
        super()._fetch_all()
        if getattr(self, "_as_original", False) and not getattr(
            self, "_originalized", False
        ):
            self._originalized = True
            self._result_cache = [item.instance for item in self._result_cache]

    def filter(self, *args, **kwargs):
        """
        This handles two special cases when building a filter queryset:

        1. You may get a filter kwargs containing "pk" (DRF does this).  This is
           interpreted as the backing table's primary key, however in our case that means
           it is the Historical model's history_id.  The caller wants to query on the
           original table's primary key, not ours.  One should query on history_id if
           one wants to find a specific historical record.

        2. If the query contains an as_of expression we properly handle it based
           on whether this is an as_original queryset or a historical one.  The
           historical one does not drop deleted records, and the as_original one does.
        """
        as_of = kwargs.pop("as_of", None)
        if as_of:
            self._as_of_filter(
                as_of, drop_deletions=getattr(self, "_as_original", False)
            )

        pk = kwargs.pop("pk", None)
        if pk:
            kwargs[self._pk_attr] = pk

        return super().filter(*args, **kwargs)

    def _as_of_filter(self, date, drop_deletions, **kwargs):
        """Return a HistoricalQuerySet containing a filter as of the specified
        timestamp.  Additional filter arguments can also be passed in.

        For additional history on this topic, see:
        https://github.com/jazzband/django-simple-history/pull/229
        https://github.com/jazzband/django-simple-history/issues/354
        https://github.com/jazzband/django-simple-history/issues/397
        """
        queryset = super().filter(history_date__lte=date, **kwargs)
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
        if drop_deletions:
            latest_historics = latest_historics.exclude(history_type="-").order_by(
                self._pk_attr
            )
        return latest_historics


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

    def as_of(self, date, **kwargs):
        """Get a snapshot as of a specific date.

        Additional filter arguments can be passed in.

        Returns an instance, or an iterable of the instances, of the
        original model with all the attributes set according to what
        was present on the object on the date provided.
        """
        if not self.instance:
            return self._as_of_set(date, **kwargs)
        queryset = self.get_queryset().filter(history_date__lte=date, **kwargs)
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

    def _as_of_set(self, date, **kwargs):
        for historic_item in self.get_queryset()._as_of_filter(
            date, drop_deletions=True, **kwargs
        ):
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
