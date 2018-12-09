# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0014_auto_20170523_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighbor',
            name='mailchimp_subscriber_id',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
