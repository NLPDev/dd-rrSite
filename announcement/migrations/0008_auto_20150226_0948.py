# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import announcement.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0007_auto_20150212_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='is_cancelled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='announcement',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=b'announcements/%Y/%m/%d', validators=[announcement.models.validate_photo]),
            preserve_default=True,
        ),
    ]
