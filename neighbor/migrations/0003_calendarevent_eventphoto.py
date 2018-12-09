# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_calendar'),
        ('neighbor', '0002_neighbor_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=100)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.TextField(null=True, blank=True)),
                ('first_name', models.CharField(max_length=40)),
                ('last_name', models.CharField(max_length=40)),
                ('phone', models.CharField(max_length=12)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('calendar', models.ForeignKey(to='community.Calendar')),
                ('neighbor', models.ForeignKey(to='neighbor.Neighbor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=b'/events/%Y/%m/%d', blank=True)),
                ('event', models.ForeignKey(to='neighbor.CalendarEvent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
