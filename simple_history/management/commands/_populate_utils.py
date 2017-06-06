from django.utils.timezone import now


class NotHistorical(TypeError):
    """No related history model found."""


def get_history_model_for_model(model):
    """Find the history model for a given app model."""
    try:
        manager_name = model._meta.simple_history_manager_attribute
    except AttributeError:
        raise NotHistorical("Cannot find a historical model for "
                            "{model}.".format(model=model))
    return getattr(model, manager_name).model


def bulk_history_create(model, history_model, batch_size):
    """Save a copy of all instances to the historical model."""
    historical_instances = [
        history_model(
            history_date=getattr(instance, '_history_date', now()),
            history_user=getattr(instance, '_history_user', None),
            **{
                field.attname: getattr(instance, field.attname)
                for field in instance._meta.fields
            }
        ) for instance in model.objects.all()]
    history_model.objects.bulk_create(historical_instances, batch_size=batch_size)
