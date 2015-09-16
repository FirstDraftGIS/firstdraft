# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0005_delete_geoname'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geonameid', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('asciiname', models.CharField(max_length=200, null=True, blank=True)),
                ('alternatenames', models.CharField(max_length=10000, null=True, blank=True)),
                ('latitude', models.DecimalField(max_digits=50, decimal_places=10)),
                ('longitude', models.DecimalField(max_digits=50, decimal_places=10)),
                ('feature_class', models.CharField(max_length=1)),
                ('feature_code', models.CharField(max_length=10)),
                ('country_code', models.CharField(max_length=2)),
                ('cc2', models.CharField(max_length=2)),
                ('admin1_code', models.CharField(max_length=20)),
                ('admin2_code', models.CharField(max_length=80)),
                ('admin3_code', models.CharField(max_length=20)),
                ('admin4_code', models.CharField(max_length=20)),
                ('population', models.IntegerField()),
                ('elevation', models.IntegerField()),
                ('dem', models.IntegerField()),
                ('timezone', models.CharField(max_length=40)),
                ('modification_date', models.DateField()),
            ],
        ),
    ]
