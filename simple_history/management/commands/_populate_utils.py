from django import db
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


def bulk_history_create(
        log_file, model, history_model, batch_size):
    """Save a copy of all instances to the historical model.
    :param log_file: file object used to log to, can pass sys.stdout for
        logging to cmdline
    :param model: Model you want to bulk create
    :param history_model: History Model to bulk create
    :param batch_size: number of models to create at once.
    :return:
    """

    historical_instances = []

    log_file.write(
        "Starting bulk creating history models for {} instances {}-{}"
            .format(model, 0, batch_size)
    )
    for index, instance in enumerate(model.objects.iterator()):
        # Can't Just pass batch_size to bulk_create as this can lead to
        # Out of Memory Errors as we load too many models into memory after
        # creating them. So we only keep batch_size worth of models in
        # historical_instances and clear them after we hit batch_size
        if index % batch_size == 0:

            history_model.objects.bulk_create(
                historical_instances, batch_size=batch_size
            )

            historical_instances = []
            # you need reset_queries as Django in debug mode will keep track
            # on all your sql statements for debugging purposes.
            db.reset_queries()
            log_file.write(
                "Finished bulk creating history models for {} instances "
                "{}-{}, starting next {}"
                    .format(model, index - batch_size, index, batch_size)
            )

        historical_instances.append(
            history_model(
                history_date=getattr(instance, '_history_date', now()),
                history_user=getattr(instance, '_history_user', None),
                **{
                    field.attname: getattr(instance, field.attname)
                    for field in instance._meta.fields
                }
            )
        )

    # create any we didn't get in the last loop
    if historical_instances:
        history_model.objects.bulk_create(
            historical_instances, batch_size=batch_size
        )
