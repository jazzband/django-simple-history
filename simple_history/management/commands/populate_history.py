from __future__ import unicode_literals, print_function

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now
from optparse import make_option
from django.db import transaction, models as db_models
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


COMMAND_HINT = "Please specify a model or use the --auto option"


class NotHistorical(TypeError):
    """No related history model found."""


class Command(BaseCommand):
    args = "<app.model app.model ...>"
    help = ("Populates the corresponding HistoricalRecords field with "
            "the current state of all instances in a model")

    option_list = BaseCommand.option_list + (
        make_option(
            '--auto',
            action='store_true',
            dest='auto',
            default=False,
            help="Automatically search for models with the "
                 "HistoricalRecords field type",
        ),
    )

    def handle(self, *args, **options):
        models = db_models.get_models()
        is_success = False
        if args:
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                model_string = "{app}.{model}".format(
                    app=content_type.app_label,
                    model=content_type.model,
                )
                if model_string in args:
                    try:
                        self._check_and_save(model)
                    except NotHistorical:
                        self.stdout.write(
                            "HistoricalRecords field does not exist in the "
                            "model {model}.".format(model=model.__name__)
                        )
                    else:
                        is_success = True
        elif options['auto']:
            self.stdout.write("Searching for models with the "
                              "HistoricalRecords field..")
            for model in models:
                try:
                    self._check_and_save(model)
                except NotHistorical:
                    pass
                else:
                    is_success = True
            if not is_success:
                self.stdout.write("No model with HistoryDescriptor "
                                  "field was found")
        else:
            self.stdout.write(COMMAND_HINT)

    def _check_and_save(self, model):
        """Look up the historical manager and save a copy of all
        instances to the historical model.

        """
        try:
            manager_name = model._meta.simple_history_manager_attribute
        except AttributeError:
            raise NotHistorical("Cannot find a historical model for "
                                "{model}".format(model=model))
        history_klass = getattr(model, manager_name).model
        self.stdout.write("Found HistoricalRecords field "
                          "in model {model}".format(model=model.__name__))
        historical_instances = [
            history_klass(
                history_date=getattr(instance, '_history_date', now()),
                history_user=getattr(instance, '_history_user', None),
                **{field.attname: getattr(instance, field.attname)
                   for field in instance._meta.fields}
            ) for instance in model.objects.all()]
        self.stdout.write("Saving {count} instances..".format(count=len(historical_instances)))
        try:
            history_klass.objects.bulk_create(historical_instances)
        except AttributeError:  # pragma: no cover
            # bulk_create was added in Django 1.4, handle legacy versions
            with transaction.commit_on_success():
                for instance in historical_instances:
                    instance.save()
