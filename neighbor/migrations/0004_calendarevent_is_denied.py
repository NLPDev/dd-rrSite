# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0003_calendarevent_eventphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendarevent',
            name='is_denied',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
