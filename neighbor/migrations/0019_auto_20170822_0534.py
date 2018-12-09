# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0018_auto_20170818_0705'),
    ]

    operations = [
        migrations.AddField(
            model_name='realproperty',
            name='contact',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='realproperty',
            name='lot_number',
            field=models.CharField(max_length=5),
            preserve_default=True,
        ),
    ]
