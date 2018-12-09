# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0005_auto_20150211_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarevent',
            name='description',
            field=models.TextField(null=True, verbose_name=b'Event Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='end_date',
            field=models.DateTimeField(verbose_name=b'End Time'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='location',
            field=models.CharField(max_length=100, verbose_name=b'Event Location'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='start_date',
            field=models.DateTimeField(verbose_name=b'Start Time'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='title',
            field=models.CharField(max_length=50, verbose_name=b'Event Title'),
            preserve_default=True,
        ),
    ]
