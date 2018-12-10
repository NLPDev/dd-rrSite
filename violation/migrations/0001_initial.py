# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('neighbor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Violation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40)),
                ('fee', models.DecimalField(max_digits=9, decimal_places=2)),
                ('days_to_pay', models.IntegerField(default=b'30', max_length=3)),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Violation',
                'verbose_name_plural': 'Violations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ViolationEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('violator_address', models.CharField(max_length=100)),
                ('message', models.TextField(null=True, verbose_name=b'Violation Description', blank=True)),
                ('submitted_on', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('event_date_not_relevant', models.BooleanField(default=False)),
                ('event_month', models.IntegerField(blank=True, max_length=2, null=True, choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')])),
                ('event_day', models.IntegerField(blank=True, max_length=2, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31)])),
                ('event_start', models.TimeField(null=True, blank=True)),
                ('event_end', models.TimeField(null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False, verbose_name=b'Approved')),
                ('is_denied', models.BooleanField(default=False, verbose_name=b'Denied')),
                ('is_paid', models.BooleanField(default=False, verbose_name=b'Paid')),
                ('transaction', models.ForeignKey(blank=True, to='neighbor.Transactions', null=True)),
                ('violation', models.ForeignKey(to='violation.Violation')),
                ('violator', models.ForeignKey(blank=True, to='neighbor.Neighbor', null=True)),
            ],
            options={
                'verbose_name': 'Violation Event',
                'verbose_name_plural': 'Violation Events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ViolationFaq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(default=100)),
                ('message', models.TextField()),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Violation FAQ',
                'verbose_name_plural': 'Violation FAQs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ViolationStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(default=100)),
                ('message', models.TextField()),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Violation Reporting Step',
                'verbose_name_plural': 'Violation Reporting Steps',
            },
            bases=(models.Model,),
        ),
    ]
