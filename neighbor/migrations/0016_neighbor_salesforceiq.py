# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0015_neighbor_mailchimp_subscriber_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighbor',
            name='salesforceiq_id',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
