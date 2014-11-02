# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
import simple_history.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DoYouKnow',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalYar',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', auto_created=True, db_index=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical yar',
                'ordering': ('-history_date', '-history_id'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WhatIMean',
            fields=[
                ('doyouknow_ptr', models.OneToOneField(primary_key=True, to='migration_test_app.DoYouKnow', auto_created=True, parent_link=True, serialize=False)),
            ],
            options={
            },
            bases=('migration_test_app.doyouknow',),
        ),
        migrations.CreateModel(
            name='Yar',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('what', models.ForeignKey(to='migration_test_app.WhatIMean')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='historicalyar',
            name='what_id',
            field=simple_history.models.CustomForeignKeyField(to='migration_test_app.WhatIMean', blank=True, null=True, related_name='+'),
            preserve_default=True,
        ),
    ]
