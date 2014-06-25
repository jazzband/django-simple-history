from __future__ import print_function

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from ... import models
from . import _populate_utils as utils


class Command(BaseCommand):
    args = "<app.model app.model ...>"
    help = ("Populates the corresponding HistoricalRecords field with "
            "the current state of all instances in a model")

    COMMAND_HINT = "Please specify a model or use the --auto option"
    MODEL_NOT_FOUND = "Unable to find model"
    MODEL_NOT_HISTORICAL = "No history model found"
    NO_REGISTERED_MODELS = "No registered models were found"
    START_SAVING_FOR_MODEL = "Starting saving historical records for {model}"
    DONE_SAVING_FOR_MODEL = "Finished saving historical records for {model}"

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
        to_process = set()

        if args:
            for model_pair in self._handle_model_list(*args):
                to_process.add(model_pair)

        elif options['auto']:
            for model in models.registered_models.values():
                try:    # avoid issues with mutli-table inheritance
                    history_model = utils.get_history_model_for_model(model)
                except utils.NotHistorical:
                    continue
                to_process.add((model, history_model))
            if not to_process:
                self.stdout.write(self.NO_REGISTERED_MODELS)

        else:
            self.stdout.write(self.COMMAND_HINT)

        self._process(to_process)

    def _handle_model_list(self, *args):
        failing = False
        for natural_key in args:
            try:
                model, history = self._model_from_natural_key(natural_key)
            except ValueError as e:
                self.stderr.write("{error}".format(error=e))
            else:
                if not failing:
                    yield (model, history)
        if failing:
            raise CommandError

    def _model_from_natural_key(self, natural_key):
        model = get_model(*natural_key.split(".", 1))
        if not model:
            raise ValueError(self.MODEL_NOT_FOUND +
                             " < {model} >".format(model=natural_key))
        try:
            history_model = utils.get_history_model_for_model(model)
        except utils.NotHistorical:
            raise ValueError(self.MODEL_NOT_HISTORICAL +
                             " < {model} >".format(model=natural_key))
        return model, history_model

    def _process(self, to_process):
        for model, history_model in to_process:
            self.stdout.write(self.START_SAVING_FOR_MODEL.format(model=model))
            utils.bulk_history_create(model, history_model)
            self.stdout.write(self.DONE_SAVING_FOR_MODEL.format(model=model))
