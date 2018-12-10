# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0005_community_zip_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='mailchimp_neighborhood_id',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
