from django.utils import timezone
from django.db import transaction

from . import populate_history
from ... import models, utils
from ...exceptions import NotHistoricalModelError

get_model = populate_history.get_model


class Command(populate_history.Command):
    args = "<app.model app.model ...>"
    help = (
        "Scans HistoricalRecords for identical sequencial entries "
        "(duplicates) in a model and deletes them."
    )

    DONE_CLEANING_FOR_MODEL = "Removed {count} historical records for {model}\n"

    def add_arguments(self, parser):
        parser.add_argument("models", nargs="*", type=str)
        parser.add_argument(
            "--auto",
            action="store_true",
            dest="auto",
            default=False,
            help="Automatically search for models with the HistoricalRecords field "
            "type",
        )
        parser.add_argument(
            '-d', '--dry',
            action='store_true',
            help='Dry (test) run only, no changes'
        )
        parser.add_argument(
            '-m', '--minutes',
            type=int,
            help='Only search the last MINUTES of history'
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]

        to_process = set()
        model_strings = options.get("models", []) or args

        if model_strings:
            for model_pair in self._handle_model_list(*model_strings):
                to_process.add(model_pair)

        elif options["auto"]:
            for model in models.registered_models.values():
                try:  # avoid issues with mutli-table inheritance
                    history_model = utils.get_history_model_for_model(model)
                except NotHistoricalModelError:
                    continue
                to_process.add((model, history_model))
            if not to_process:
                if self.verbosity >= 1:
                    self.stdout.write(self.NO_REGISTERED_MODELS)

        else:
            if self.verbosity >= 1:
                self.stdout.write(self.COMMAND_HINT)

        self._process(to_process, date_back=options['minutes'], dry_run=options['dry'])

    def _process(self, to_process, date_back=None, dry_run=True):
        if date_back:
            stop_date = timezone.now() - timezone.timedelta(minutes=date_back)
        else:
            stop_date = None

        for model, history_model in to_process:
            m_qs = history_model.objects
            if stop_date:
                m_qs = m_qs.filter(history_date__gte=stop_date)
            found = m_qs.count()
            if self.verbosity >= 2:
                self.stdout.write("{0} has {1} historical entries".format(model, found))
            if not found:
                continue

            # it would be great if we could just iterate over the instances that
            # have changes (in the given period) but
            # `m_qs.values(model._meta.pk.name).distinct()`
            # is actually slower than looping all and filtering in the code...
            for o in model.objects.all():
                self._process_instance(o, model, stop_date=stop_date, dry_run=dry_run)

    def _process_instance(self, instance, model, stop_date=None, dry_run=True):
        entries_deleted = 0
        o_qs = instance.history.all()
        if stop_date:
            # to compare last history match
            extra_one = o_qs.filter(history_date__lte=stop_date).first()
            o_qs = o_qs.filter(history_date__gte=stop_date)
        else:
            extra_one = None
        with transaction.atomic():
            # ordering is ('-history_date', '-history_id') so this is ok
            f1 = o_qs.first()
            if not f1:
                return

            for f2 in o_qs[1:]:
                entries_deleted += self._check_and_delete(f1, f2, dry_run)
                f1 = f2
            if extra_one:
                entries_deleted += self._check_and_delete(f1, extra_one, dry_run)
        if self.verbosity >= 1:
            self.stdout.write(self.DONE_CLEANING_FOR_MODEL.format(
                model=model, count=entries_deleted
            ))

    def _check_and_delete(self, entry1, entry2, dry_run=True):
        delta = entry1.diff_against(entry2)
        if not delta.changed_fields:
            if not dry_run:
                entry1.delete()
            return 1
        return 0