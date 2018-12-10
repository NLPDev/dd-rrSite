# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        #('neighbor', '0002_auto_20150227_1554'),
        ('violation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='violationevent',
            name='submitted_by',
            field=models.ForeignKey(related_name='submitted_by_neighbor', default=1, to='neighbor.Neighbor'),
            preserve_default=False,
        ),
    ]
