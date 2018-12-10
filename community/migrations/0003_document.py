# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import community.models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_calendar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', models.FileField(upload_to=community.models.document_filename)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Community Document',
                'verbose_name_plural': 'Community Documents',
            },
            bases=(models.Model,),
        ),
    ]
