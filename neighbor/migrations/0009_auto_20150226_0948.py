# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import neighbor.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0008_addressconflict'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendarevent',
            name='photo',
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='is_cancelled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='duepayment',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name=b'Active'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='duepayment',
            name='is_due',
            field=models.BooleanField(default=True, verbose_name=b'Due'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='duepayment',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name=b'Paid'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventphoto',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=b'calendar/%Y/%m/%d', validators=[neighbor.models.validate_photo]),
            preserve_default=True,
        ),
    ]
