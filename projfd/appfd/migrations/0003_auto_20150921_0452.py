# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0002_place_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='admin1_code',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='place',
            name='admin2_code',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
