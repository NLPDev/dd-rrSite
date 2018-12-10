# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import service_provider.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('neighbor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, verbose_name=b'Service Description', blank=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=service_provider.models.thumbnail_file_name, blank=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Service Title')),
                ('phone', models.CharField(max_length=12, null=True, verbose_name=b'Phone Number', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, verbose_name=b'E-mail Address', blank=True)),
                ('website', models.CharField(max_length=255, null=True, blank=True)),
                ('facebook', models.CharField(max_length=255, null=True, blank=True)),
                ('twitter', models.CharField(max_length=255, null=True, blank=True)),
                ('linkedin', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus', models.CharField(max_length=255, null=True, blank=True)),
                ('sort_order', models.IntegerField(default=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_denied', models.BooleanField(default=False)),
                ('community', models.ForeignKey(to='community.Community')),
                ('neighbor', models.ForeignKey(blank=True, to='neighbor.Neighbor', null=True)),
            ],
            options={
                'verbose_name': 'Service Provider',
                'verbose_name_plural': 'Service Providers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('community', models.ForeignKey(to='community.Community')),
            ],
            options={
                'verbose_name': 'Service Type',
                'verbose_name_plural': 'Service Types',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='type',
            field=models.ForeignKey(to='service_provider.ServiceType'),
            preserve_default=True,
        ),
    ]
