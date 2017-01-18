from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

try:
    from django.apps import apps
except ImportError:  # Django < 1.7
    from django.db.models.loading import get_model
else:
    get_model = apps.get_model

from ... import models
from . import _populate_utils as utils


class Command(BaseCommand):
    args = "<app.model app.model ...>"
    help = ("Populates the corresponding HistoricalRecords field with "
            "the current state of all instances in a model")

    COMMAND_HINT = "Please specify a model or use the --auto option"
    MODEL_NOT_FOUND = "Unable to find model"
    MODEL_NOT_HISTORICAL = "No history model found"
    NO_REGISTERED_MODELS = "No registered models were found\n"
    START_SAVING_FOR_MODEL = "Saving historical records for {model}\n"
    DONE_SAVING_FOR_MODEL = "Finished saving historical records for {model}\n"
    EXISTING_HISTORY_FOUND = "Existing history found, skipping model"
    INVALID_MODEL_ARG = "An invalid model was specified"

    if hasattr(BaseCommand, 'option_list'):  # Django < 1.8
        option_list = BaseCommand.option_list + (
            make_option('--auto', action='store_true', dest='auto', default=False),
        )

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('models', nargs='*', type=str)
        parser.add_argument(
            '--auto',
            action='store_true',
            dest='auto',
            default=False,
            help='Automatically search for models with the '
                 'HistoricalRecords field type',
        )

    def handle(self, *args, **options):
        to_process = set()
        model_strings = options.get('models', []) or args

        if model_strings:
            for model_pair in self._handle_model_list(*model_strings):
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
                failing = True
                self.stderr.write("{error}\n".format(error=e))
            else:
                if not failing:
                    yield (model, history)
        if failing:
            raise CommandError(self.INVALID_MODEL_ARG)

    def _model_from_natural_key(self, natural_key):
        try:
            app_label, model = natural_key.split(".", 1)
        except ValueError:
            model = None
        else:
            try:
                model = get_model(app_label, model)
            except LookupError:  # Django >= 1.7
                model = None
        if not model:
            raise ValueError(self.MODEL_NOT_FOUND +
                             " < {model} >\n".format(model=natural_key))
        try:
            history_model = utils.get_history_model_for_model(model)
        except utils.NotHistorical:
            raise ValueError(self.MODEL_NOT_HISTORICAL +
                             " < {model} >\n".format(model=natural_key))
        return model, history_model

    def _process(self, to_process):
        for model, history_model in to_process:
            if history_model.objects.count():
                self.stderr.write("{msg} {model}\n".format(
                    msg=self.EXISTING_HISTORY_FOUND,
                    model=model,
                ))
                continue
            self.stdout.write(self.START_SAVING_FOR_MODEL.format(model=model))
            utils.bulk_history_create(model, history_model)
            self.stdout.write(self.DONE_SAVING_FOR_MODEL.format(model=model))
