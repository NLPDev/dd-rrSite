# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0007_calendarevent_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressConflict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('new_neighbor_first', models.CharField(max_length=50)),
                ('new_neighbor_last', models.CharField(max_length=50)),
                ('new_neighbor_phone', models.CharField(max_length=50)),
                ('new_neighbor_email', models.EmailField(max_length=256)),
                ('is_resolved', models.BooleanField(default=False)),
                ('existing_neighbor', models.ForeignKey(to='neighbor.Neighbor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
