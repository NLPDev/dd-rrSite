# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0002_auto_20150130_1654'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40)),
                ('display_order', models.IntegerField(default=1)),
                ('is_public', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='announcement',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=b'announcements/%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='announcement',
            name='tags',
            field=models.ManyToManyField(to='announcement.Tag', null=True, blank=True),
            preserve_default=True,
        ),
    ]
