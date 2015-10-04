# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0008_auto_20150926_0021'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternateName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geonameid', models.IntegerField(db_index=True)),
                ('isolanguage', models.CharField(max_length=7, null=True, blank=True)),
                ('alternate_name', models.CharField(db_index=True, max_length=200, null=True, blank=True)),
                ('isPreferredName', models.CharField(max_length=1, null=True, blank=True)),
                ('isShortName', models.CharField(max_length=1, null=True, blank=True)),
                ('isColloquial', models.CharField(max_length=1, null=True, blank=True)),
                ('isHistoric', models.CharField(max_length=1, null=True, blank=True)),
            ],
        ),
    ]
