# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0019_auto_20170822_0534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realproperty',
            name='address_2',
            field=models.CharField(default=b'', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='realproperty',
            name='city',
            field=models.CharField(default=b'', max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='realproperty',
            name='contact',
            field=models.CharField(default=b'', max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
