# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0004_announcement_is_denied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='content',
            field=models.TextField(verbose_name=b'Description'),
            preserve_default=True,
        ),
    ]
