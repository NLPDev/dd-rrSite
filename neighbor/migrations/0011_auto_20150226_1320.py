# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0010_auto_20150226_1208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transactions',
            options={'verbose_name': 'Transaction', 'verbose_name_plural': 'Transactions'},
        ),
    ]
