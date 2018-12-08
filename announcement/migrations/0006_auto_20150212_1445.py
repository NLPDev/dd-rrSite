# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0005_auto_20150212_1441'),
    ]

    operations = [
        migrations.RenameField(
            model_name='announcement',
            old_name='date',
            new_name='event_date',
        ),
    ]
