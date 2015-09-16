# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0008_auto_20150914_0403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoname',
            name='cc2',
            field=models.CharField(max_length=200),
        ),
    ]
