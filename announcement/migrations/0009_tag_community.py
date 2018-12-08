# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_auto_20150226_0948'),
        ('announcement', '0008_auto_20150226_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='community',
            field=models.ForeignKey(default=1, to='community.Community'),
            preserve_default=False,
        ),
    ]
