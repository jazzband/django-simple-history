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
