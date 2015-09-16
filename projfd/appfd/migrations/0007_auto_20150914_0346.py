# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0006_geoname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geoname',
            name='id',
        ),
        migrations.AlterField(
            model_name='geoname',
            name='geonameid',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
