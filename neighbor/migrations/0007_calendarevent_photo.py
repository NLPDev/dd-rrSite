# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0006_auto_20150212_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendarevent',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=b'calendar/%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
    ]
