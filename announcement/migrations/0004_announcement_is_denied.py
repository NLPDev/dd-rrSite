# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0003_auto_20150204_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='is_denied',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
