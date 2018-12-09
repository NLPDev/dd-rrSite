# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
        ('dues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cards',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=15, choices=[(b'V', b'VISA'), (b'MC', b'MASTERCARD'), (b'AMEX', b'AMERICAN EXPRESS'), (b'D', b'DISCOVER')])),
                ('last_four', models.IntegerField(max_length=4)),
                ('exp_date', models.DateField()),
                ('token', models.CharField(max_length=60)),
                ('billing_name', models.CharField(max_length=50)),
                ('billing_address_1', models.CharField(max_length=50)),
                ('billing_address_2', models.CharField(max_length=50, null=True, blank=True)),
                ('billing_city', models.CharField(max_length=50)),
                ('billing_state', models.CharField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('billing_zipcode', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DuePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('is_due', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('dues', models.ForeignKey(to='dues.Dues')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Neighbor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.CharField(max_length=20, null=True, blank=True)),
                ('address_1', models.CharField(max_length=100, null=True, blank=True)),
                ('address_2', models.CharField(max_length=100, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zip_code', models.CharField(max_length=10, null=True, blank=True)),
                ('preferred_contact_method', models.CharField(blank=True, max_length=20, null=True, choices=[(b'email', b'Email'), (b'phone', b'Phone')])),
                ('community', models.ForeignKey(related_name='Community', blank=True, to='community.Community', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('transaction_type', models.CharField(max_length=2, choices=[(b'V', b'VIOLATION'), (b'R', b'RESERVATION'), (b'D', b'DUES')])),
                ('amount', models.DecimalField(max_digits=9, decimal_places=2)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('neighbor', models.ForeignKey(to='neighbor.Neighbor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='transactions',
            name='wallet',
            field=models.ForeignKey(to='neighbor.Wallet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='duepayment',
            name='neighbor',
            field=models.ForeignKey(to='neighbor.Neighbor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cards',
            name='wallet',
            field=models.ForeignKey(to='neighbor.Wallet'),
            preserve_default=True,
        ),
    ]
