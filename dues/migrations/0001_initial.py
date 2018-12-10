# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dues',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pay_frequency', models.CharField(max_length=2, choices=[(b'M', b'Monthly'), (b'Y', b'Yearly')])),
                ('fee', models.DecimalField(default=0.0, max_digits=9, decimal_places=2)),
                ('late_fee', models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)),
                ('late_fee_period', models.IntegerField(help_text=b'Reoccurs after x days (i.e. $10 every month)', null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=40)),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Due',
                'verbose_name_plural': 'Dues',
            },
            bases=(models.Model,),
        ),
    ]
