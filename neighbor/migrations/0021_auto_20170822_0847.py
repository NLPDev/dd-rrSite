# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0020_auto_20170822_0557'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='realproperty',
            unique_together=set([('community', 'lot_number')]),
        ),
    ]
