from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage, Paginator
from django.db.models import QuerySet
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from .forms import ReadOnlyFieldsMixin, new_readonly_form

__all__ = (
    'MissingHistoryRecordsField',
    'HistoryRecordListViewMixin',
    'RevertFromHistoryRecordViewMixin'
)


class MissingHistoryRecordsField(Exception):
    """django-simple-history is somehow improperly configured"""
    pass


class HistoryRecordListViewMixin(object):
    """
    A mixin for views manipulating multiple django-simple-history HistoricalRecords of object.
    """
    history_records_allow_empty = True
    history_records_queryset = None
    history_records_paginate_by = None
    history_records_paginate_orphans = 0
    history_records_context_object_name = None
    history_records_paginator_class = Paginator
    history_records_page_kwarg = 'hpage'
    history_records_ordering = None
    history_records_object_list = None

    def get_history_records_field_name(self):
        """
        Return the model HistoricalRecords field name to use get the history queryset.
        """
        if hasattr(self.model._meta, 'simple_history_manager_attribute'):
            return self.model._meta.simple_history_manager_attribute
        else:
            raise MissingHistoryRecordsField(
                "The model %(cls)s does not have a HistoryRecords field. Define a HistoryRecords()"
                " field into %(cls)s model class, after do this, run:"
                "\npython manage.py makemigrations %(app_label)s"
                "\npython manage.py migrate %(app_label)s"
                "\npython manage.py populate_history %(app_label)s.%(cls)s " % {
                    'app_label': self.model._meta.app_label,
                    'cls': self.model.__name__
                }
            )

    def get_history_records_queryset(self):
        """
        Return the list of history_records items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.history_records_queryset is not None:
            queryset = self.history_records_queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            model_instance = self.get_object()
            queryset = getattr(model_instance, self.get_history_records_field_name()).all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a HistoryRecords QuerySet. Define "
                "%(cls)s.history_records_queryset, "
                " or override %(cls)s.get_history_records_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_history_records_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_history_records_ordering(self):
        """
        Return the field or fields to use for ordering the history_records queryset.
        """
        return self.history_records_ordering

    def paginate_history_records_queryset(self, queryset, page_size):
        """
        Paginate the history_records queryset, if needed.
        """
        paginator = self.get_history_records_paginator(
            queryset, page_size, orphans=self.get_history_records_paginate_orphans(),
            allow_empty_first_page=self.get_history_records_allow_empty())
        page_kwarg = self.history_records_page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(
                    _("HistoryRecords Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid HistoryRecords page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_history_records_paginate_by(self, queryset):
        """
        Get the number of history_records items to paginate by, or ``None`` for no pagination.
        """
        return self.history_records_paginate_by

    def get_history_records_paginator(self, queryset, per_page, orphans=0,
                                      allow_empty_first_page=True, **kwargs):
        """
        Return an instance of the history_records paginator for this view.
        """
        return self.history_records_paginator_class(
            queryset, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page, **kwargs)

    def get_history_records_paginate_orphans(self):
        """
        Returns the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.history_records_paginate_orphans

    def get_history_records_allow_empty(self):
        """
        Returns ``True`` if the view should display empty history_records lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.history_records_allow_empty

    def get_history_records_context_object_name(self):
        """
        Get the name of the history_records item to be used in the context.
        """
        if self.history_records_context_object_name:
            return self.history_records_context_object_name
        elif hasattr(self, 'model'):
            return '%s_history_records_object_list' % self.model._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        history_records_queryset = kwargs.pop('history_records_object_list',
                                              self.history_records_object_list)
        history_records_page_size = self.get_history_records_paginate_by(history_records_queryset)
        history_records_context_object_name = self.get_history_records_context_object_name()
        if history_records_page_size:
            (history_records_paginator, history_records_page, history_records_queryset,
             history_records_is_paginated) = self.paginate_history_records_queryset(
                history_records_queryset, history_records_page_size)
            context = {
                'history_records_paginator': history_records_paginator,
                'history_records_page_obj': history_records_page,
                'history_records_is_paginated': history_records_is_paginated,
                'history_records_page_kwarg': self.history_records_page_kwarg,
                'history_records_object_list': history_records_queryset
            }
        else:
            context = {
                'history_records_paginator': None,
                'history_records_page_obj': None,
                'history_records_is_paginated': False,
                'history_records_page_kwarg': self.history_records_page_kwarg,
                'history_records_object_list': history_records_queryset
            }
        if history_records_context_object_name is not None:
            context[history_records_context_object_name] = history_records_queryset
        context.update(kwargs)
        return super(HistoryRecordListViewMixin, self).get_context_data(**context)

    def get(self, request, *args, **kwargs):
        self.history_records_object_list = self.get_history_records_queryset()
        history_records_allow_empty = self.get_history_records_allow_empty()

        if not history_records_allow_empty:
            # When pagination is enabled and history_records_object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_history_records_paginate_by(
                self.history_records_object_list) is not None and hasattr(
                self.history_records_object_list, 'exists')):  # noqa
                is_empty = not self.history_records_object_list.exists()
            else:
                is_empty = len(self.history_records_object_list) == 0
            if is_empty:
                raise Http404(
                    _("Empty HistoryRecords list and "
                      "'%(class_name)s.history_records_allow_empty' is False.")
                    % {'class_name': self.__class__.__name__})

        return super(HistoryRecordListViewMixin, self).get(self, request, *args, **kwargs)


class RevertFromHistoryRecordViewMixin(object):
    history_records_readonly_form = True

    def get_form_class(self):
        form_klass = super(RevertFromHistoryRecordViewMixin, self).get_form_class()
        if issubclass(form_klass, ReadOnlyFieldsMixin):
            return form_klass
        else:
            return new_readonly_form(form_klass,
                                     all_fields=self.history_records_readonly_form,
                                     readonly_fields=()
                                     )

    def get_history_records_field_name(self):
        """
        Return the model HistoricalRecords field name to use get the history queryset.
        """
        if hasattr(self.model._meta, 'simple_history_manager_attribute'):
            return self.model._meta.simple_history_manager_attribute
        else:
            raise MissingHistoryRecordsField(
                "The model %(cls)s does not have a HistoryRecords field. Define a HistoryRecords()"
                " field into %(cls)s model class, after do this, run:"
                "\npython manage.py makemigrations %(app_label)s"
                "\npython manage.py migrate %(app_label)s"
                "\npython manage.py populate_history %(app_label)s.%(cls)s " % {
                    'app_label': self.model._meta.app_label,
                    'cls': self.model.__name__
                }
            )

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(history_id=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj.instance

    def get_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the history records of object.

        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overridden.
        """
        if self.queryset is None:
            if self.model:
                queryset = getattr(self.model, self.get_history_records_field_name()).all()
                return queryset
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.queryset.all()
