# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0006_auto_20150212_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='event_date',
            field=models.DateField(),
            preserve_default=True,
        ),
    ]
