# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('neighbor', '0001_initial'),
        ('announcement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='community',
            field=models.ForeignKey(to='community.Community'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='announcement',
            name='neighbor',
            field=models.ForeignKey(to='neighbor.Neighbor'),
            preserve_default=True,
        ),
    ]
