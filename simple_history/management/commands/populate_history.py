from __future__ import unicode_literals, print_function

from optparse import make_option

from django.db import models as db_models
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from simple_history.manager import HistoryDescriptor


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Populates the corresponding HistoricalRecords field with the current state of all instances in a model'

    option_list = BaseCommand.option_list + (
        make_option('--auto',
            action = 'store_true',
            dest = 'auto',
            default = False,
            help = 'Automatically search for models with the HistoricalRecords field type'),
        )

    def handle(self, *args, **options):
        models = db_models.get_models()
        is_success = False
        if args:
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                if "{app}.{model}".format(app=content_type.app_label, model=content_type.model) in args:
                    if self._check_and_save(model):
                        is_success = True
                    else:
                        print('HistoricalRecords field does not exist in the model %s.' % model.__name__)
        elif options['auto']:
            print('Searching for models with the HistoricalRecords field..')
            for model in models:
                if self._check_and_save(model):
                    is_success = True
            if not is_success:
                print('No model with HistoryDescriptor field was found')
        else:
            print('Please specify a model or use the --auto option')
        if is_success:
            print('Command executed successfully')

    def _check_and_save(self, model):
        ''' Checks if a HistoricalRecords field exists in the model '''
        ''' Calls the save() method on all of the model's instances '''
        has_history = False
        for field in model.__dict__:
            if type(model.__dict__[field]) == HistoryDescriptor:
                print('Found HistoricalRecords field in model %s' % model.__name__)
                instances = model.objects.all()
                print('Saving %d instances..' % instances.count())
                for object in instances:
                    object.save()
                has_history = True
        return has_history
