# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0005_auto_20150921_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='admin_level',
            field=models.IntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='geonameid',
            field=models.IntegerField(db_index=True, null=True, blank=True),
        ),
    ]
