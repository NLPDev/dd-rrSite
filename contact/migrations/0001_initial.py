# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighbor', '0013_auto_20150227_1547'),
        ('community', '0005_community_zip_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100, null=True, blank=True)),
                ('last_name', models.CharField(max_length=100, null=True, blank=True)),
                ('phone', models.CharField(max_length=20, null=True, blank=True)),
                ('email', models.CharField(max_length=100, null=True, blank=True)),
                ('message', models.TextField(max_length=1000)),
                ('preferred_method', models.CharField(default=b'email', max_length=10, verbose_name=b'Preferred Contact Method', choices=[(b'email', b'Email'), (b'phone', b'Phone')])),
                ('date', models.DateTimeField()),
                ('community', models.ForeignKey(to='community.Community')),
                ('neighbor', models.ForeignKey(to='neighbor.Neighbor')),
            ],
            options={
                'ordering': ('-date', 'first_name', 'last_name'),
                'verbose_name': 'Contact Lead',
                'verbose_name_plural': 'Contact Leads',
            },
            bases=(models.Model,),
        ),
    ]
