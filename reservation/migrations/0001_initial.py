# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0001_initial'),
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservableServices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40)),
                ('description', models.TextField(null=True, blank=True)),
                ('fee', models.DecimalField(default=0.0, max_digits=5, decimal_places=2)),
                ('open', models.TimeField(null=True, blank=True)),
                ('close', models.TimeField(null=True, blank=True)),
                ('turn_around_time', models.IntegerField(null=True, blank=True)),
                ('fidelity', models.CharField(default=b'1', max_length=3, choices=[(b'.25', b'15 minutes'), (b'.5', b'30 minutes'), (b'1', b'1 hour'), (b'2', b'2 hours'), (b'4', b'4 hours')])),
                ('is_approved', models.BooleanField(default=False, verbose_name=b'Approved')),
                ('community', models.ForeignKey(to='community.Community')),
                ('related_service', models.ManyToManyField(help_text=b'Related services that can be booked, like pool and pool house', related_name='related_service_rel_+', null=True, to='reservation.ReservableServices', blank=True)),
            ],
            options={
                'verbose_name': 'Reservable Service',
                'verbose_name_plural': 'Reservable Services',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReserveBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('event_description', models.TextField(null=True, blank=True)),
                ('is_paid', models.BooleanField(default=False, verbose_name=b'Paid')),
                ('is_cancelled', models.BooleanField(default=False)),
                ('neighbor', models.ForeignKey(to='neighbor.Neighbor')),
                ('service', models.ForeignKey(to='reservation.ReservableServices')),
                ('transaction', models.ForeignKey(blank=True, to='neighbor.Transactions', null=True)),
            ],
            options={
                'verbose_name': 'Reserved Time',
                'verbose_name_plural': 'Reserved Times',
            },
            bases=(models.Model,),
        ),
    ]
