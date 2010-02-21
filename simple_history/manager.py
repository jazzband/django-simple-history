from django.db import models

class HistoryDescriptor(object):
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

    def get_query_set(self):
        if self.instance is None:
            return super(HistoryManager, self).get_query_set()

        filter = {self.instance._meta.pk.name: self.instance.pk}
        return super(HistoryManager, self).get_query_set().filter(**filter)

    def most_recent(self):
        """
        Returns the most recent copy of the instance available in the history.
        """
        if not self.instance:
            raise TypeError("Can't use most_recent() without a %s instance." % \
                            self.instance._meta.object_name)
        fields = (field.name for field in self.instance._meta.fields)
        try:
            values = self.values_list(*fields)[0]
        except IndexError:
            raise self.instance.DoesNotExist("%s has no historical record." % \
                                             self.instance._meta.object_name)
        return self.instance.__class__(*values)

    def as_of(self, date):
        """
        Returns an instance of the original model with all the attributes set
        according to what was present on the object on the date provided.
        """
        if not self.instance:
            raise TypeError("Can't use as_of() without a %s instance." % \
                            self.instance._meta.object_name)
        fields = (field.name for field in self.instance._meta.fields)
        qs = self.filter(history_date__lte=date)
        try:
            values = qs.values_list('history_type', *fields)[0]
        except IndexError:
            raise self.instance.DoesNotExist("%s had not yet been created." % \
                                             self.instance._meta.object_name)
        if values[0] == '-':
            raise self.instance.DoesNotExist("%s had already been deleted." % \
                                             self.instance._meta.object_name)
        return self.instance.__class__(*values[1:])
