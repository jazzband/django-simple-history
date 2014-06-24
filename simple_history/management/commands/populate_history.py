from __future__ import unicode_literals, print_function

from optparse import make_option
from django.db import models as db_models
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from ...manager import HistoryDescriptor
from ... import models


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
                    if self._check_and_save(model):
                        is_success = True
                    else:
                        self.stdout.write(
                            "HistoricalRecords field does not exist in the "
                            "model {model}.".format(model=model.__name__)
                        )
        elif options['auto']:
            self.stdout.write("Searching for models with the "
                              "HistoricalRecords field..")
            for model in models:
                if self._check_and_save(model):
                    is_success = True
            if not is_success:
                self.stdout.write("No model with HistoryDescriptor "
                                  "field was found")
        else:
            self.stdout.write('Please specify a model or use the --auto option')
        if is_success:
            self.stdout.write('Command executed successfully')

    def _check_and_save(self, model):
        """Checks if a HistoricalRecords field exists in the model

        Calls the save() method on all of the model's instances

        """
        for name, attr in model.__dict__.items():
            if isinstance(attr, HistoryDescriptor):
                self.stdout.write("Found HistoricalRecords field "
                                  "in model {model}".format(model=model.__name__))
                instances = list(model.objects.all())
                self.stdout.write("Saving {count} instances..".format(count=len(instances)))
                for instance in instances:
                    models.HistoricalRecords.create_historical_record(
                        instance=instance,
                        type="~",
                        manager_name=name,
                    )
        else:
            return False
        return True
