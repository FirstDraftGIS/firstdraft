# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0009_auto_20150914_0405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoname',
            name='dem',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='geoname',
            name='population',
            field=models.BigIntegerField(),
        ),
    ]
