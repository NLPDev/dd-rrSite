# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0009_auto_20150226_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='transaction_type',
            field=models.CharField(max_length=2, choices=[(b'V', b'DUES/VIOLATIONS'), (b'R', b'RESERVATION')]),
            preserve_default=True,
        ),
    ]
