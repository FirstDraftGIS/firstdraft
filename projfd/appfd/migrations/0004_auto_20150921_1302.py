# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0003_auto_20150921_0452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='admin1_code',
            field=models.CharField(db_index=True, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='admin2_code',
            field=models.CharField(db_index=True, max_length=100, null=True, blank=True),
        ),
    ]
