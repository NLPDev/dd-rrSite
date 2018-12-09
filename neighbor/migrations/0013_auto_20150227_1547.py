# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0012_auto_20150227_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neighbor',
            name='address_1',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
