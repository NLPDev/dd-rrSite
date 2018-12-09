# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0004_calendarevent_is_denied'),
    ]

    operations = [
        migrations.AddField(
            model_name='cards',
            name='security_code',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='duepayment',
            name='transaction',
            field=models.ForeignKey(blank=True, to='neighbor.Transactions', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transactions',
            name='failure_code',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transactions',
            name='failure_message',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transactions',
            name='stripe_id',
            field=models.CharField(max_length=b'200', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transactions',
            name='stripe_paid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='neighbor',
            name='address_1',
            field=models.CharField(max_length=100, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
