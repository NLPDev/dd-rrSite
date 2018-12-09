# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0011_auto_20150226_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseReport',
            fields=[
            ],
            options={
                'verbose_name': 'Purchase Report',
                'proxy': True,
                'verbose_name_plural': 'Purchase Report',
            },
            bases=('neighbor.transactions',),
        ),
        migrations.AlterModelOptions(
            name='calendarevent',
            options={'verbose_name': 'Calendar Event', 'verbose_name_plural': 'Calendar Events'},
        ),
    ]
